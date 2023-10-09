export PROJECT_ID=$PROJECT_ID
export TEMPLATE=template.txt
export LLM_TEMPLATE=${LLM_TEMPLATE:-llm_template.txt}

export SLACK_OAUTH_TOKEN=$(gcloud --project=$PROJECT_ID secrets versions access --secret=slack_oauth_token latest)
export SLACK_CHANNEL_ID=$(gcloud --project=$PROJECT_ID secrets versions access --secret=slack_channel latest)
if [ -z $SLACK_OAUTH_TOKEN ] || [ -z $SLACK_CHANNEL_ID ];
then
  echo "can not get Slack parameter"
  exit 1
fi

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
PORT=${SLACK_ROUTING_PORT:-8800}
docker build -t $NAME .
docker stop $NAME
docker rm $NAME
CMD="docker run -d --name $NAME --restart always -p $PORT:8080 -e SLACK_OAUTH_TOKEN=$SLACK_OAUTH_TOKEN -e SLACK_CHANNEL_ID=$SLACK_CHANNEL_ID -e TEMPLATE=$TEMPLATE -e LLM_TEMPLATE=$LLM_TEMPLATE -v $(pwd)/config:/config $NAME"
echo $CMD
$CMD
