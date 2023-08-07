export SLACK_OAUTH_TOKEN=$(gcloud secrets versions access --secret=slack_oauth_token latest)
export SLACK_CHANNEL_ID=$(gcloud secrets versions access --secret=slack_channel latest)
export TEMPLATE=template.txt

export PYENV_ROOT="$HOME/.pyenv"
export PATH=$PATH:$HOME/.pyenv/shims
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

cd ~/repos/slack-routine-notifying
poetry run python main.py
