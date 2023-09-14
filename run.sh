export SLACK_OAUTH_TOKEN=$(gcloud --project=$PROJECT_ID secrets versions access --secret=slack_oauth_token latest)
export SLACK_CHANNEL_ID=$(gcloud --project=$PROJECT_ID secrets versions access --secret=slack_channel latest)
export TEMPLATE=template.txt

export PYENV_ROOT="$HOME/.pyenv"
export PATH=$PATH:$HOME/.pyenv/shims
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

# cli mode
# cd ~/repos/slack-routine-notifying
# poetry run python main.py
docker run -d --restart always -p 8600:8080 -e SLACK_OAUTH_TOKEN=$SLACK_OAUTH_TOKEN -e SLACK_CHANNEL_ID=$SLACK_CHANNEL_ID -e TEMPLATE=$TEMPLATE slack-routing
