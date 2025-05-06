# Pull base image.
FROM rockylinux:8

# Specifies which defines.conf file is copied into the container,
# set as required via "docker build --build-arg VENUE=[ops|uat|sit|dev|test] ..."
ARG VENUE=ops

USER root

# Install packages
RUN dnf -y update --security \
    && dnf -y install 'dnf-command(config-manager)' && dnf config-manager --set-enabled powertools \
    && dnf -y install epel-release \
    && dnf -y install python3.11 python3.11-pip python3.11-devel python3.11-numpy python3-mod_wsgi \
      gcc yum-utils git tmux vim emacs-nox net-tools httpd \
      openssl-devel bzip2-devel libxml2-devel udunits2-devel libxslt-devel \
      httpd-devel libaec-devel netcdf-devel sqlite-devel \
      hdf5 hdf5-devel hdf5-static nbdkit-gzip-filter perl-PerlIO-gzip libtirpc-devel \
      logrotate cronie patch Xvfb urw-fonts libXext udunits2-devel \
    && dnf -y groupinstall "Development Tools" \
    && dnf -y install texlive cairo-devel dejavu-sans-fonts \
    && dnf -y localinstall https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox-0.12.6.1-2.almalinux8.x86_64.rpm \
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
COPY --chmod=644 requirements.txt /tmp/
COPY --chmod=644 requirements-checkers.txt /tmp/

RUN pip3.11 install --upgrade pip \
    && pip3.11 install -r /tmp/requirements.txt /tmp/requirements-checkers.txt mod_wsgi==4.9.4 \
    && mod_wsgi-express install-module > /etc/httpd/conf.modules.d/02-wsgi.conf

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

ENV PATH "$PATH:/var/www/html/mcc"
ENV PATH "$PATH:/var/www/html/mcc/web"
ENV PYTHONPATH "${PYTHONPATH}:/var/www/html/mcc"
ENV PYTHONPATH "${PYTHONPATH}:/var/www/html/mcc/web"

# Setup wkhtmltopdf stuff
RUN echo -e '#!/bin/bash\nxvfb-run -a --server-args="-screen 0, 1024x768x24" /usr/local/bin/wkhtmltopdf -q $*' > /usr/local/bin/wkhtmltopdf.sh \
    && chmod a+x /usr/local/bin/wkhtmltopdf.sh \
    && ln -s /usr/local/bin/wkhtmltopdf.sh /home/mcc/bin/wkhtmltopdf

# Make sure the wkhtmltopdf wrapper gets precedence in the path
ENV PATH "/home/mcc/bin:$PATH"

# Link apache config to container logs
RUN ln -sf /proc/self/fd/1 /var/log/httpd/error_log

# Add daily scripts to crontab and remove the default weekly Apache logrotate job
RUN crontab -l | { cat; echo "0 0 * * * run-parts /etc/cron.daily"; } | crontab - \
    && sed -i 's/^/#/' /etc/httpd/conf.d/welcome.conf \
    && rm /etc/logrotate.d/httpd

CMD ["/bin/bash", "/home/mcc/start_mcc.sh"]
