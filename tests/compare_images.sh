#!/usr/bin/env bash
#
# compare_images.sh: side-by-side regression check of two MCC images.
#
# Starts both images locally and sends every file in tests/data through ACDD, CF and GDS2
# (every version/level) as JSON, plus HTML and PDF, then reports any difference between
# the two images' output. It also inspects the NEW image: removed/required packages,
# Python dependency versions, missing shared libraries, and the app import.
#
# Usage:
#   tests/compare_images.sh OLD_IMAGE NEW_IMAGE [OUTPUT_DIR]
#
# Example (deployed 1.6.1 vs. a local OPS build of 1.6.2):
#   docker build --platform linux/amd64 --pull --no-cache --build-arg VENUE=ops -t podaac/mcc:1.6.2-ops .
#   tests/compare_images.sh "$REGISTRY/podaac/mcc@sha256:ed1037e05fc297bc1727664a42685bcf32f26089ae25f7b438d9e02ab6039159" \
#       podaac/mcc:1.6.2-ops
#
# Example (SIT build of 1.6.2 vs. the deployed OPS 1.6.1 image):
#   IGNORE_VENUE=1 tests/compare_images.sh "$OPS_REGISTRY/podaac/mcc@sha256:ed1037e0..." "$SIT_REGISTRY/podaac/mcc:1.6.2"
#
# Options (environment variables):
#   MAX_MB=60            skip test files larger than this many MB (default: no limit)
#   IGNORE_VENUE=1       ignore the homepage URL and venue name, so that images built for
#                        different venues can be compared (e.g. a SIT build of 1.6.2 against
#                        the deployed OPS 1.6.1 image)
#   PLATFORM=linux/amd64 docker platform for both images
#   OLD_PORT=18081 NEW_PORT=18082   local ports
#
# Requires docker, curl and jq >= 1.6 (macOS: brew install jq). Build both images for the
# same VENUE so their defines (homepage URL, size limits) match, or set IGNORE_VENUE=1.
# Exit status: 0 if every output matches and every image check passes; 1 otherwise.

set -u

# Byte-wise sorting and matching throughout: comm needs both RPM lists sorted the same way,
# and macOS sed/grep otherwise reject bytes that aren't valid UTF-8.
export LC_ALL=C

OLD=${1:?usage: $0 OLD_IMAGE NEW_IMAGE [OUTPUT_DIR]}
NEW=${2:?usage: $0 OLD_IMAGE NEW_IMAGE [OUTPUT_DIR]}
OUT=${3:-compare-$(date +%Y%m%d-%H%M%S)}
PLATFORM=${PLATFORM:-linux/amd64}
OLD_PORT=${OLD_PORT:-18081}
NEW_PORT=${NEW_PORT:-18082}
MAX_MB=${MAX_MB:-0}
IGNORE_VENUE=${IGNORE_VENUE:-0}
DATA_DIR="$(cd "$(dirname "$0")/data" && pwd)"

for cmd in docker curl jq; do
    command -v "$cmd" >/dev/null 2>&1 || { echo "Missing required command: $cmd" >&2; exit 2; }
done

mkdir -p "$OUT/old" "$OUT/new" "$OUT/diff"
SUMMARY="$OUT/summary.txt"
: > "$SUMMARY"
FAILURES=0

log()    { echo "$*" | tee -a "$SUMMARY"; }
record() { # status label detail
    printf '%-5s %-70s %s\n' "$1" "$2" "$3" | tee -a "$SUMMARY"
    [ "$1" = "PASS" ] || FAILURES=$((FAILURES + 1))
}

cleanup() { docker rm -f mcc-compare-old mcc-compare-new >/dev/null 2>&1; }
trap cleanup EXIT

start_container() { # name image port
    docker rm -f "$1" >/dev/null 2>&1
    docker run -d --rm --platform "$PLATFORM" --name "$1" -p "$3:8080" "$2" >/dev/null \
        || { echo "Could not start $2" >&2; exit 2; }
}

wait_ready() { # port
    for _ in $(seq 1 90); do
        curl -fsS -o /dev/null --max-time 5 "http://localhost:$1/" && return 0
        sleep 2
    done
    return 1
}

# Normalizers: remove values that legitimately differ between runs or versions.
#  - "hash" fields are random per run (cf_shim.py: hash(name) + randrange(1e5))
#  - each upload is saved under a random temporary name (/tmp/mcc/tmpXXXXXXXX), which some
#    checker messages include
#  - the checkers build some multi-line messages from Python sets, whose order changes each
#    time Apache starts (Python randomizes string hashing per process). The lines within a
#    message (JSON) or a <pre> block (HTML) are sorted, so only their order is ignored.
#  - mcc_version differs by design
#  - with IGNORE_VENUE=1: the homepage URL (https://mcc.podaac[.sit|.uat].earthdatacloud.nasa.gov)
#    and the venue name in the page footer
TMP_RE='/tmp/mcc/tmp[A-Za-z0-9_]{8}'
norm_json() {
    jq -S --arg tmp "$TMP_RE" 'del(.mcc_version?) | walk(
          if type == "object" then del(.hash)
          elif type == "string" then gsub($tmp; "/tmp/mcc/TMP") | split("\n") | sort | join("\n")
          else . end)' "$1" 2>/dev/null || norm_text "$1"
}
norm_text() {
    if [ "$IGNORE_VENUE" = "1" ]; then
        sed -E -e 's#https?://mcc\.podaac\.(sit\.|uat\.)?earthdatacloud\.nasa\.gov#HOMEPAGE#g' \
               -e 's#(footer_env">)(SIT|UAT|OPS)<#\1VENUE<#g' "$1"
    else
        cat "$1"
    fi | sed -E -e "s#$TMP_RE#/tmp/mcc/TMP#g" -e 's/-?[0-9]{6,}/N/g' -e 's/1\.6\.[0-9]+/1.6.X/g' \
       | sort_pre_blocks
}
# Sorts the lines inside each <pre>...</pre> block (see the notes above).
sort_pre_blocks() {
    awk '
        function flush(   i, j, t) {
            for (i = 2; i <= n; i++) {            # insertion sort: blocks are short
                t = buf[i]
                for (j = i - 1; j >= 1 && buf[j] > t; j--) buf[j + 1] = buf[j]
                buf[j + 1] = t
            }
            for (i = 1; i <= n; i++) print buf[i]
            n = 0
        }
        {
            line = $0 ""
            if (!inpre && (p = index(line, "<pre>")) > 0) {
                print substr(line, 1, p + 4)
                line = substr(line, p + 5)
                inpre = 1; n = 0
            }
            if (inpre) {
                if ((p = index(line, "</pre>")) > 0) {
                    if (p > 1) buf[++n] = substr(line, 1, p - 1)
                    flush()
                    print substr(line, p)
                    inpre = 0
                } else {
                    buf[++n] = line
                }
                next
            }
            print
        }
        END { if (inpre) flush() }'
}
# Number of page objects. wkhtmltopdf writes each "/Type /Page" on its own line, ending the line
# right after "Page" ("/Pages" is the page tree, not a page).
pdf_pages() { local n; n=$(grep -a -c -E '/Type[[:space:]]*/Page([^s]|$)' "$1" 2>/dev/null); echo "${n:-0}"; }

# request OUTFILE URL CURL_ARGS... -> prints "<http_code> <content_type>"
request() {
    local out=$1 url=$2; shift 2
    curl -sS -o "$out" -w '%{http_code} %{content_type}' --max-time 1800 "$@" "$url" 2>>"$OUT/curl-errors.log"
}

# compare LABEL KIND PATH [CURL_ARGS...]
#   KIND: json | html | pdf
compare() {
    local label=$1 kind=$2 path=$3; shift 3
    local safe; safe=$(printf "%s" "$label" | tr -c 'A-Za-z0-9._-' '_')
    # Saved with the response type as the extension (.json, .html, .pdf) so they open directly.
    local o="$OUT/old/$safe.$kind" n="$OUT/new/$safe.$kind"

    # Run the same request against both containers in parallel.
    ( request "$o" "http://localhost:$OLD_PORT$path" "$@" > "$o.meta" ) &
    ( request "$n" "http://localhost:$NEW_PORT$path" "$@" > "$n.meta" ) &
    wait

    local mo mn so sn; mo=$(cat "$o.meta"); mn=$(cat "$n.meta"); so=${mo%% *}; sn=${mn%% *}
    if [ "$so" != "$sn" ]; then
        record FAIL "$label" "HTTP status old=$so new=$sn"
        return
    fi
    if [ "$kind" = "pdf" ] && [ "$sn" = "200" ]; then
        local po pn; po=$(pdf_pages "$o"); pn=$(pdf_pages "$n")
        if [ "$pn" = "0" ] || [ "$po" != "$pn" ]; then
            record FAIL "$label" "PDF pages old=$po new=$pn (review old/$safe.pdf and new/$safe.pdf)"
        else
            record PASS "$label" "HTTP 200, $pn page(s); review side by side: old/$safe.pdf new/$safe.pdf"
        fi
        return
    fi
    case "$kind" in
        json) norm_json "$o" > "$o.norm"; norm_json "$n" > "$n.norm" ;;
        *)    norm_text "$o" > "$o.norm"; norm_text "$n" > "$n.norm" ;;  # html, or a non-200 pdf error page
    esac
    if diff -u "$o.norm" "$n.norm" > "$OUT/diff/$safe.diff"; then
        rm -f "$OUT/diff/$safe.diff"
        record PASS "$label" "HTTP ${mn%% *}"
    else
        record FAIL "$label" "output differs: diff/$safe.diff"
    fi
}

# --------------------------------------------------------------------------------------
log "MCC image comparison  $(date)"
log "OLD: $OLD"
log "NEW: $NEW"
log ""

start_container mcc-compare-old "$OLD" "$OLD_PORT"
start_container mcc-compare-new "$NEW" "$NEW_PORT"
wait_ready "$OLD_PORT" || { echo "OLD image did not become ready" >&2; docker logs mcc-compare-old | tail -50; exit 2; }
wait_ready "$NEW_PORT" || { echo "NEW image did not become ready" >&2; docker logs mcc-compare-new | tail -50; exit 2; }

log "== Pages"
for page in / /about /about_api; do
    compare "GET $page" html "$page"
done

log ""
log "== Request validation (expect identical 400 responses)"
SMALL="$DATA_DIR/tdset.h5"
compare "no response field" json /check -F CF=on -F "file-upload=@$SMALL"
compare "no checker selected" json /check -F response=json -F "file-upload=@$SMALL"
compare "invalid response type" json /check -F response=xml -F CF=on -F "file-upload=@$SMALL"

log ""
log "== Checks (every file in tests/data)"
# Version/level combinations: together they cover every ACDD and CF version and GDS2 level.
COMBOS="ACDD-1.1:CF-1.6:L2P ACDD-1.3:CF-1.7:L3 ACDD-1.3:CF-1.8:L4 ACDD-1.3:CF-1.9:L2P"
for f in "$DATA_DIR"/*; do
    [ -f "$f" ] || continue
    name=$(basename "$f")
    if [ "$MAX_MB" -gt 0 ] && [ "$(wc -c < "$f" | tr -d " ")" -gt $((MAX_MB * 1024 * 1024)) ]; then
        log "SKIP  $name (larger than MAX_MB=$MAX_MB)"
        continue
    fi
    for combo in $COMBOS; do
        acdd=${combo%%:*}; rest=${combo#*:}; cf=${rest%%:*}; gds=${rest#*:}
        form="-F ACDD=on -F ACDD-version=${acdd#ACDD-} -F CF=on -F CF-version=${cf#CF-} -F GDS2=on -F GDS2-parameter=$gds"
        # shellcheck disable=SC2086
        compare "$name $combo json" json /check -F response=json $form -F "file-upload=@$f"
    done
    form="-F ACDD=on -F ACDD-version=1.3 -F CF=on -F CF-version=1.9 -F GDS2=on -F GDS2-parameter=L2P"
    # shellcheck disable=SC2086
    compare "$name ACDD-1.3:CF-1.9:L2P html" html /check -F response=html $form -F "file-upload=@$f"
    # shellcheck disable=SC2086
    compare "$name ACDD-1.3:CF-1.9:L2P pdf" pdf /check -F response=pdf $form -F "file-upload=@$f"
done

docker logs mcc-compare-old > "$OUT/old/container.log" 2>&1
docker logs mcc-compare-new > "$OUT/new/container.log" 2>&1

# --------------------------------------------------------------------------------------
log ""
log "== NEW image checks"
image_check() { # label expected-substring command
    local label=$1 expect=$2 cmd=$3 result
    result=$(docker run --rm --platform "$PLATFORM" --entrypoint bash "$NEW" -c "$cmd" 2>&1)
    echo "$result" > "$OUT/new/check-$(printf "%s" "$label" | tr -c 'A-Za-z0-9._-' '_').txt"
    if echo "$result" | grep -q -- "$expect"; then record PASS "$label" ""; else record FAIL "$label" "$(echo "$result" | tail -3 | tr '\n' ' ')"; fi
}

image_check "pip check" "No broken requirements" "python3.11 -m pip check"
image_check "app imports (Flask 3 JSON provider)" "IMPORT_OK" \
    "cd / && ApiMaxFileSize=1000 UiMaxFileSize=1000 HomepageURL=http://localhost Venue=TEST TempFileLocation=/tmp \
     python3.11 -c \"import sys; sys.path.append('/var/www/html/mcc'); from web.server import app; print('IMPORT_OK')\""
image_check "removed packages are absent" "ALL_ABSENT" \
    "present=''; for p in xorg-x11-server-Xvfb libXfont2 git tmux vim-enhanced vim-minimal emacs-nox texlive \
       java-1.8.0-openjdk-headless openssh-clients openssh ghostscript poppler gcc gdb python3-mod_wsgi; do \
       rpm -q \$p >/dev/null 2>&1 && present=\"\$present \$p\"; done; \
     [ -z \"\$present\" ] && echo ALL_ABSENT || echo \"still installed:\$present\""
image_check "runtime packages are present" "ALL_PRESENT" \
    "rpm -q httpd python3.11 python3.11-numpy udunits2 wkhtmltox cronie logrotate >/dev/null && echo ALL_PRESENT"
image_check "no missing shared libraries" "NO_MISSING_LIBS" \
    "missing=\$( { ldd /usr/local/bin/wkhtmltopdf; \
                  find /usr/local/lib/python3.11 /usr/local/lib64/python3.11 /usr/lib64/httpd/modules -name '*.so*' -exec ldd {} \\; ; } 2>/dev/null | grep 'not found' | sort -u ); \
     [ -z \"\$missing\" ] && echo NO_MISSING_LIBS || echo \"\$missing\""
image_check "pre-commit, virtualenv, filelock removed" "NONE_INSTALLED" \
    "python3.11 -m pip show pre-commit virtualenv filelock 2>&1 | grep -q '^Name:' && echo 'still installed' || echo NONE_INSTALLED"
image_check "no requirements files left in /tmp" "TMP_CLEAN" \
    "ls /tmp/requirements*.txt /tmp/build/*.txt 2>/dev/null | grep -q . && echo 'found leftovers' || echo TMP_CLEAN"
image_check "upgraded Python package versions (see file)" "Name:" \
    "python3.11 -m pip show flask werkzeug requests urllib3 setuptools certifi idna soupsieve lxml pip | grep -E '^(Name|Version):'; \
     ls /usr/local/lib/python3.11/site-packages/setuptools/_vendor | grep -E '^(wheel|jaraco.context)-'"

# Package differences between the two images, for review.
# Sorted here rather than in the container, so both lists use the same (LC_ALL=C) order for comm.
rpm_list() { docker run --rm --platform "$PLATFORM" --entrypoint bash "$1" -c "rpm -qa --qf '%{NAME}\n'" | sort -u; }
rpm_list "$OLD" > "$OUT/old/rpms.txt"
rpm_list "$NEW" > "$OUT/new/rpms.txt"
comm -23 "$OUT/old/rpms.txt" "$OUT/new/rpms.txt" > "$OUT/rpms-removed.txt"
comm -13 "$OUT/old/rpms.txt" "$OUT/new/rpms.txt" > "$OUT/rpms-added.txt"
log ""
log "RPMs removed in NEW: $(wc -l < "$OUT/rpms-removed.txt" | tr -d ' ') (review $OUT/rpms-removed.txt)"
log "RPMs added in NEW:   $(wc -l < "$OUT/rpms-added.txt" | tr -d ' ') (review $OUT/rpms-added.txt)"

log ""
if [ "$FAILURES" -eq 0 ]; then
    log "RESULT: PASS. Also review the PDFs side by side ($OUT/old vs $OUT/new) and the RPM lists."
    exit 0
else
    log "RESULT: FAIL ($FAILURES item(s)). See $SUMMARY and $OUT/diff/."
    exit 1
fi
