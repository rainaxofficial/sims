#!/usr/bin/env bash
set -o errexit

STORAGE_DIR=/opt/render/project/.render

# Download and extract Chrome (cached)
if [[ ! -d $STORAGE_DIR/chrome ]]; then
  echo "...Downloading Chrome"
  mkdir -p $STORAGE_DIR/chrome
  cd $STORAGE_DIR/chrome
  wget -q -O chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  dpkg -x chrome.deb $STORAGE_DIR/chrome
  rm chrome.deb
  cd $HOME/project/src || cd $HOME/project
else
  echo "...Using cached Chrome"
fi

# Download and install matching ChromeDriver v138
echo "...Downloading ChromeDriver v138"
cd /opt/render/project/.render
wget -q -O chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/138.0.7204.168/linux64/chromedriver-linux64.zip
unzip -q chromedriver.zip
mv chromedriver-linux64/chromedriver .
chmod +x chromedriver
rm -rf chromedriver.zip chromedriver-linux64

# Install Python dependencies
pip install -r requirements.txt
