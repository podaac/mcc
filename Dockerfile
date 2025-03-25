# Pull base image.
# TODO: port to a non-centos based image
FROM centos/python-38-centos7

# Specifies which defines.conf file is copied into the container,
# set as required via "docker build --build-arg VENUE=[ops|uat|sit|dev|test] ..."
ARG VENUE=ops

USER root

# As of 2024, mirrorlist.centos.org doesn't exist anymore, so yum needs to be
# repointed to the new endpoint (vault.centos.org) to pull packages from.
# See https://serverfault.com/questions/1161816/mirrorlist-centos-org-no-longer-resolve/1161847#1161847
# TODO: remove once ported off of centos
RUN sed -i s/mirror.centos.org/vault.centos.org/g /etc/yum.repos.d/CentOS-*.repo \
    && sed -i s/^#.*baseurl=http/baseurl=http/g /etc/yum.repos.d/CentOS-*.repo \
    && sed -i s/^mirrorlist=http/#mirrorlist=http/g /etc/yum.repos.d/CentOS-*.repo

# Install yum packages
RUN yum -y update --security \
    && yum -y install epel-release \
    && yum -y install gcc yum-utils curl git tmux vim emacs-nox openssl-devel bzip2-devel libxml2-devel udunits2-devel libxslt-devel \
    && yum -y install python3-mod_wsgi httpd-devel libaec-devel dnf net-tools apache2 netcdf-devel sqlite-devel hdf5-devel \
    && yum -y install nbdkit-plugin-gzip perl-PerlIO-gzip hdf-devel \
    && yum -y install logrotate cronie patch wkhtmltopdf Xvfb urw-fonts libXext \
    && yum -y install udunits2-devel \
    && yum -y install texlive \
    && yum -y groupinstall "Development Tools" \
    && yum -y install cairo-devel dejavu-sans-fonts \
    && yum clean all

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

RUN pip install --upgrade pip \
    && pip install -r /tmp/requirements.txt \
    && pip install -r /tmp/requirements-checkers.txt \
    && pip install mod_wsgi==4.9.4 \
    && mod_wsgi-express install-module > /etc/httpd/conf.modules.d/02-wsgi.conf

# This needs to be set to allow Apache/Python to write to the temp directory
RUN usermod -u 1000 apache

# modify apache to bind to 8080 instead of 80
RUN sed -i "s/Listen 80/Listen 8080/g" /etc/httpd/conf/httpd.conf

# expose apache port
EXPOSE 8080

# Copy script files
RUN mkdir -p -m 755 /var/www/html/mcc /home/mcc

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
RUN echo -e '#!/bin/bash\nxvfb-run -a --server-args="-screen 0, 1024x768x24" /usr/bin/wkhtmltopdf -q $*' > /usr/bin/wkhtmltopdf.sh \
    && chmod a+x /usr/bin/wkhtmltopdf.sh \
    && ln -s /usr/bin/wkhtmltopdf.sh /usr/local/bin/wkhtmltopdf

# Link apache config to container logs
RUN ln -sf /proc/self/fd/1 /var/log/httpd/error_log

# Add daily scripts to crontab and remove the default weekly Apache logrotate job
RUN crontab -l | { cat; echo "0 0 * * * run-parts /etc/cron.daily"; } | crontab - \
    && sed -i 's/^/#/' /etc/httpd/conf.d/welcome.conf \
    && rm /etc/logrotate.d/httpd

CMD ["/bin/bash", "/home/mcc/start_mcc.sh"]
