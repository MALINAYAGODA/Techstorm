FROM golang:1.22

WORKDIR /app

COPY . .

RUN go mod download

# Install Chromium using Rod's toolkit
RUN go run github.com/go-rod/rod/lib/utils/get-browser

# Install Chromium's dependencies (from https://github.com/go-rod/rod/blob/main/lib/docker/Dockerfile)
RUN apt-get update > /dev/null && \
    apt-get install --no-install-recommends -y \
    # chromium dependencies
    libnss3 \
    libxss1 \
    libasound2 \
    libxtst6 \
    libgtk-3-0 \
    libgbm1 \
    ca-certificates \
    # fonts
    fonts-liberation fonts-noto-color-emoji fonts-noto-cjk \
    # timezone
    tzdata \
    # process reaper
    dumb-init \
    # headful mode support, for example: $ xvfb-run chromium-browser --remote-debugging-port=9222
    xvfb \
    > /dev/null && \
    # cleanup
    rm -rf /var/lib/apt/lists/*

RUN go build -o /service /app/cmd/service

EXPOSE 8080

ENTRYPOINT [ "/service" ]