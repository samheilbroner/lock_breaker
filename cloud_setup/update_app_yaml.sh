#!/bin/bash

CLOUD_SQL_CONNECTION_STRING="$PROJECT_ID:$REGION:$INSTANCE_NAME"

# Specify the path to your app.yaml file
APP_YAML_PATH="./app.yaml"

# Check if beta_settings with cloud_sql_instances already exists
EXISTING_SETTING=$(grep "cloud_sql_instances:" $APP_YAML_PATH)

if [ -z "$EXISTING_SETTING" ]; then
  # Check if beta_settings block already exists
  BETA_SETTINGS_EXIST=$(grep "beta_settings:" $APP_YAML_PATH)

  if [ -z "$BETA_SETTINGS_EXIST" ]; then
    # beta_settings block doesn't exist, add it along with cloud_sql_instances
    echo -e "\nbeta_settings:\n  cloud_sql_instances: \"$CLOUD_SQL_CONNECTION_STRING\"" >> $APP_YAML_PATH
    echo "Added beta_settings with cloud_sql_instances to $APP_YAML_PATH."
  else
    # beta_settings block exists, add cloud_sql_instances under it
    sed -i "" "/beta_settings:/a \\cloud_sql_instances: \"$CLOUD_SQL_CONNECTION_STRING\"" $APP_YAML_PATH
  echo "Added cloud_sql_instances to existing beta_settings in $APP_YAML_PATH."
  fi
else
  # cloud_sql_instances setting already exists, update it
  sed -i "" "s|cloud_sql_instances: \".*\"|cloud_sql_instances: \"$CLOUD_SQL_CONNECTION_STRING\"|g" $APP_YAML_PATH
  echo "Updated cloud_sql_instances in $APP_YAML_PATH."
fi

