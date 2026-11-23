# MCC Dockerfile.
# Originally reconstructed from the build history of the deployed 1.6.1 image
# (podaac/mcc:1.6.1, sha256:ed1037e05fc297bc1727664a42685bcf32f26089ae25f7b438d9e02ab6039159),
# whose Dockerfile was never committed; 1.6.2 applies the ECR vulnerability fixes on top.
#
# Base image: Rocky Linux 8.10 (the 1.6.1 image was built from Rocky 8.9).
# Rocky's maintained images are published as rockylinux/rockylinux. If this tag is unavailable,
# rockylinux:8.9 works too: the "dnf -y upgrade" below brings it to 8.10.
FROM rockylinux/rockylinux:8.10

# Specifies which defines.conf file is copied into the container,
# set as required via "docker build --build-arg VENUE=[ops|uat|sit|dev|test] ..."
ARG VENUE=ops

USER root

# Install dnf packages
# Apply all available updates (not just --security): every OS finding in the 1.6.1
# Inspector report is fixed by a published Rocky 8.10 update.
# Not installed because MCC doesn't use them (each carried Inspector findings): git, tmux,
# vim, emacs-nox, texlive, python3-mod_wsgi (built for Python 3.6; Apache loads the
# Python 3.11 mod_wsgi installed by pip). vim-minimal, from the base image, is removed.
# Optional ("weak") dependencies are not installed; they brought in Java (via jna).
RUN echo "install_weak_deps=False" >> /etc/dnf/dnf.conf \
    && dnf -y upgrade --refresh \
    && dnf -y install 'dnf-command(config-manager)' && dnf config-manager --set-enabled powertools \
    && dnf -y install epel-release \
    && dnf -y install python3.11 python3.11-pip python3.11-devel python3.11-numpy \
      gcc yum-utils net-tools httpd \
      openssl-devel bzip2-devel libxml2-devel udunits2-devel libxslt-devel \
      httpd-devel libaec-devel netcdf-devel sqlite-devel \
      hdf5 hdf5-devel hdf5-static nbdkit-gzip-filter perl-PerlIO-gzip libtirpc-devel \
      logrotate cronie patch urw-fonts libXext udunits2-devel \
    && dnf -y groupinstall "Development Tools" \
    && dnf -y install cairo-devel dejavu-sans-fonts \
    && dnf -y localinstall https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox-0.12.6.1-2.almalinux8.x86_64.rpm \
    && if rpm -q vim-minimal >/dev/null; then dnf -y remove vim-minimal; fi \
    && dnf clean all

# Install udunits
RUN curl -O https://downloads.unidata.ucar.edu/udunits/2.2.28/udunits-2.2.28.tar.gz \
	&& tar xzf udunits-2.2.28.tar.gz \
	&& cd udunits-2.2.28 \
	&& /bin/sh configure --prefix=/usr/local \
	&& make -j \
	&& make install \
	&& cd .. \
	&& rm -rf udunits-2.2.28 \
	&& rm -rf udunits-2.2.28.tar.gz

ENV C_INCLUDE_PATH=/usr/include/udunits2/:$C_INCLUDE_PATH
ENV C_INCLUDE_PATH=/usr/local/lib/:$C_INCLUDE_PATH
ENV UDUNITS2_LIBS=/usr/include/udunits2/:$UDUNITS2_LIBS
ENV UDUNITS2_LIBS=/usr/local/lib/:$UDUNITS2_LIBS
ENV UDUNITS2_INCLUDE=/usr/local/lib:$UDUNITS2_INCLUDE

# Install Python modules and mod_wsgi
# - The requirements files are bind-mounted for this step only, so no copies are left in the
#   image (Inspector also flagged the pins in the old /tmp/requirements*.txt copies).
# - constraints.txt pins every other package to the version running in 1.6.1, so a clean
#   build only changes the packages deliberately updated in requirements*.txt.
# - "pip check" fails the build if the installed packages have conflicting requirements.
RUN --mount=type=bind,source=requirements.txt,target=/tmp/build/requirements.txt \
    --mount=type=bind,source=requirements-checkers.txt,target=/tmp/build/requirements-checkers.txt \
    --mount=type=bind,source=constraints.txt,target=/tmp/build/constraints.txt \
    pip3.11 install --upgrade pip \
    && pip3.11 install -c /tmp/build/constraints.txt \
         -r /tmp/build/requirements.txt -r /tmp/build/requirements-checkers.txt mod_wsgi==4.9.4 \
    && pip3.11 check \
    && mod_wsgi-express install-module > /etc/httpd/conf.modules.d/02-wsgi.conf

# Remove compilers and development packages now that the Python packages are built.
# The compiled Python packages ship their own libraries; at runtime they need only base
# system libraries plus udunits2 (for cf_units). Runtime packages are marked as explicitly
# installed first, because dnf also removes packages that were only pulled in as
# dependencies, and udunits2 was installed only as a dependency of udunits2-devel.
RUN dnf mark install httpd python3.11 python3.11-libs python3.11-pip python3.11-numpy udunits2 wkhtmltox \
    && dnf -y remove gcc python3.11-devel openssl-devel bzip2-devel libxml2-devel udunits2-devel \
         libxslt-devel httpd-devel libaec-devel netcdf-devel sqlite-devel \
         hdf5 hdf5-devel hdf5-static libtirpc-devel cairo-devel \
    && dnf -y groupremove "Development Tools" \
    && dnf clean all

# This needs to be set to allow Apache/Python to write to the temp directory
RUN usermod -u 1000 apache

# modify apache to bind to 8080 instead of 80
RUN sed -i "s/Listen 80/Listen 8080/g" /etc/httpd/conf/httpd.conf

# expose apache port
EXPOSE 8080

# Copy script files
RUN mkdir -p -m 755 /var/www/html/mcc /home/mcc/bin

COPY --chmod=755 mcc /var/www/html/mcc/
COPY --chmod=644 VERSION /var/www/html/mcc/web/
COPY --chmod=755 start_mcc.sh /home/mcc/
COPY --chmod=644 mcc_wsgi.conf /home/mcc/
COPY --chmod=644 env/sample_defines/defines.$VENUE.conf /home/mcc/defines.conf
COPY --chmod=644 env/sample_defines/logrotate.conf /home/mcc/

# Setup environment defines and Apache/logrotate config
RUN echo "Include /home/mcc/defines.conf" >> /etc/httpd/conf/httpd.conf \
    && echo "Include /home/mcc/mcc_wsgi.conf" >> /etc/httpd/conf/httpd.conf \
    && echo "ServerName 127.0.0.1" >> /etc/httpd/conf/httpd.conf \
    && echo 'LoadModule headers_module modules/mod_headers.so' >> /etc/httpd/conf/httpd.conf \
    && echo '<IfModule mod_headers.c>' >> /etc/httpd/conf/httpd.conf \
    && echo '    Header always edit Set-Cookie (.*) "$1; HttpOnly; Secure."' >> /etc/httpd/conf/httpd.conf \
    && echo '</IfModule>' >> /etc/httpd/conf/httpd.conf

ENV PATH="$PATH:/var/www/html/mcc"
ENV PATH="$PATH:/var/www/html/mcc/web"
ENV PYTHONPATH="${PYTHONPATH}:/var/www/html/mcc"
ENV PYTHONPATH="${PYTHONPATH}:/var/www/html/mcc/web"

# wkhtmltopdf: no xvfb-run wrapper. The wkhtmltox build ("with patched qt") renders
# without an X server, and MCC calls /usr/local/bin/wkhtmltopdf directly (server.py).

# Link apache config to container logs
RUN ln -sf /proc/self/fd/1 /var/log/httpd/error_log

# Add daily scripts to crontab and remove the default weekly Apache logrotate job
RUN crontab -l | { cat; echo "0 0 * * * run-parts /etc/cron.daily"; } | crontab - \
    && sed -i 's/^/#/' /etc/httpd/conf.d/welcome.conf \
    && rm /etc/logrotate.d/httpd

CMD ["/bin/bash", "/home/mcc/start_mcc.sh"]
