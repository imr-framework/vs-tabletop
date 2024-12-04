#!/usr/bin/bash
set -euo pipefail
# Reusing mri4all install script

VS_BASE=/opt/games
VS_USER=vagrant

error() {
  local parent_lineno="$1"
  local code="${3:-1}"
  echo "Error on or near line ${parent_lineno}"
  exit "${code}"
}
trap 'error ${LINENO}' ERR

install_linux_packages() {
  echo "## Installing Linux packages..."
  sudo apt-get update
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y build-essential make wget curl git git-lfs python3-wheel python3-dev python3 python3-venv python3-virtualenv ffmpeg libsm6 libxext6 dcmtk
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev libgdbm-dev libnss3-dev libedit-dev libc6-dev
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y virtualbox-guest-utils virtualbox-guest-x11 xfce4 xfce4-terminal
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y firefox
}

install_docker () {
  if [ ! -x "$(command -v docker)" ]; then 
    echo "## Installing Docker..."
    sudo apt-get update
    sudo apt-get remove docker docker-engine docker.io || true
    echo '* libraries/restart-without-asking boolean true' | sudo debconf-set-selections
    sudo DEBIAN_FRONTEND=noninteractive apt-get install apt-transport-https ca-certificates curl software-properties-common -y
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg |  sudo apt-key add -
    sudo apt-key fingerprint 0EBFCD88
    sudo add-apt-repository \
        "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) \
        stable" -y
    sudo apt-get update
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y docker-ce
    # Restart docker to make sure we get the latest version of the daemon if there is an upgrade
    sudo service docker restart
    # Make sure we can actually use docker as the vagrant user
    sudo usermod -a -G docker $VS_USER
    sudo docker --version
  fi

  if [ ! -x "$(command -v docker-compose)" ]; then 
    echo "## Installing Docker-Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    sudo docker-compose --version
  fi
}

create_folder () {
  if [[ ! -e $1 ]]; then
    echo "## Creating $1"
    sudo mkdir -p $1
    sudo chown $VS_USER:$VS_USER $1
    sudo chmod a+x $1
  else
    echo "## $1 already exists."
  fi
}

create_folders () {
  create_folder $VS_BASE
  # create_folder $VS_BASE/vstabletop
  # create_folder $VS_BASE/lab_manuals
  # create_folder $VS_BASE/logs  # Might use this later
}

install_games() {
  echo "## Installing vs-tabletop repositories..."
  cd $VS_BASE
  sudo su $VS_USER -c "git clone --branch delta-diy https://github.com/imr-framework/vs-tabletop vs-tabletop-main" 
  cd vs-tabletop-main
}

install_python_dependencies() {
  echo "## Installing Python runtime environment..."
  
  if [ ! -e "$VS_BASE/env" ]; then
    sudo su $VS_USER -c "mkdir \"$VS_BASE/env\""
	sudo su $VS_USER -c "python3 -m venv $VS_BASE/env"
  fi

  echo "## Installing required Python packages..."
  cd /opt/games
  sudo su $VS_USER -c "$VS_BASE/env/bin/pip install --isolated -r \"$VS_BASE/vs-tabletop-main/requirements.txt\""
}

echo ""
echo "## Installing VS games software..."
echo ""

install_linux_packages
install_docker
create_folders
install_games
install_python_dependencies

echo ""
echo "Installation complete."
echo ""
