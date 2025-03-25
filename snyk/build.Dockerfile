FROM snyk/snyk:python-3.8

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    zip \
    && apt-get clean

RUN adduser --quiet --disabled-password --shell /bin/sh --home /home/dockeruser --uid 300 dockeruser

USER dockeruser
COPY requirements.txt /home/dockeruser/
COPY requirements-checkers.txt /home/dockeruser/
WORKDIR "/home/dockeruser"
RUN pwd
RUN ls -al

RUN pip3 install --upgrade pip \
    && pip3 install awscli --upgrade
USER root
RUN apt-get -y install apache2-dev apache2

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
USER dockeruser
RUN curl -sSL https://install.python-poetry.org | python3 - --version 1.5.1

ENV PATH="${PATH}:/home/dockeruser/.local/bin"

RUN poetry --version

USER root
RUN pwd
RUN ls -al
RUN pip install -r requirements.txt
RUN pip install -r requirements-checkers.txt

CMD ["sh"]
