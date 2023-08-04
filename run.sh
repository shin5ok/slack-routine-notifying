export SLACK_OAUTH_TOKEN=$(gcloud secrets versions access --secret=slack_oauth_token latest)
export SLACK_CHANNEL_ID=$(gcloud secrets versions access --secret=slack_channel latest)
export PATH=$PATH:$HOME/.pyenv/shims

export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

cd ~/slack-routine-notifying
poetry run python main.py