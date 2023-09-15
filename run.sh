export PROJECT_ID=shingo-ar-test0729
export SLACK_OAUTH_TOKEN=$(gcloud --project=$PROJECT_ID secrets versions access --secret=slack_oauth_token latest)
export SLACK_CHANNEL_ID=$(gcloud --project=$PROJECT_ID secrets versions access --secret=slack_channel latest)
export TEMPLATE=template.txt

echo "SLACK_OAUTH_TOKEN:" $SLACK_OAUTH_TOKEN
echo "SLACK_CHANNEL_ID:" $SLACK_CHANNEL_ID

export PYENV_ROOT="$HOME/.pyenv"
export PATH=$PATH:$HOME/.pyenv/shims
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

# cli mode
# cd ~/repos/slack-routine-notifying
# poetry run python main.py


NAME=slack-routing
PORT=8800
docker build -t $NAME .
docker stop $NAME
docker rm $NAME
CMD="docker run -d --name $NAME --restart always -v $HOME/.config:/root/.config -p $PORT:8080 -e SLACK_OAUTH_TOKEN=$SLACK_OAUTH_TOKEN -e SLACK_CHANNEL_ID=$SLACK_CHANNEL_ID -e TEMPLATE=$TEMPLATE $NAME"
echo $CMD
$CMD
