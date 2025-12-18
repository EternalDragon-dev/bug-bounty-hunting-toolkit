FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Install essential packages and security tools
RUN apt-get update && apt-get install -y \
    openssh-server \
    sudo \
    curl \
    wget \
    git \
    nano \
    vim \
    htop \
    net-tools \
    iputils-ping \
    python3 \
    python3-pip \
    nodejs \
    npm \
    php \
    php-cli \
    nmap \
    netcat-openbsd \
    dnsutils \
    whois \
    traceroute \
    tcpdump \
    nikto \
    sqlmap \
    gobuster \
    dirb \
    hydra \
    john \
    hashcat \
    aircrack-ng \
    && rm -rf /var/lib/apt/lists/*

# Clone and setup Seeker
RUN cd /opt && \
    git clone https://github.com/thewhiteh4t/seeker.git && \
    cd seeker && \
    chmod +x seeker.py

# Install additional Python security tools
RUN pip3 install \
    requests \
    beautifulsoup4 \
    selenium \
    scapy \
    pwntools \
    paramiko \
    impacket \
    dnspython \
    shodan

# Create a user
RUN useradd -m -s /bin/bash vpsuser && \
    echo 'vpsuser:password123' | chpasswd && \
    usermod -aG sudo vpsuser && \
    chown -R vpsuser:vpsuser /opt/seeker

# Copy and run setup script
COPY vps-setup.sh /tmp/vps-setup.sh
RUN chmod +x /tmp/vps-setup.sh && /tmp/vps-setup.sh

# Configure SSH
RUN mkdir /var/run/sshd && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

# Expose SSH port
EXPOSE 22

# Start SSH service
CMD ["/usr/sbin/sshd", "-D"]