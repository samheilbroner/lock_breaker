execute_files_in_order() {
  for file in "$@"; do
    if [ -f "$file" ]; then
      chmod +x "$file"
      . "$file"
    else
      echo "File '$file' does not exist."
    fi
  done
}

execute_files_in_order "cloud_setup/configure_environment_variables.sh" \
                       "cloud_setup/postgres_password.sh" \
                       "cloud_setup/enable_postgres.sh" \
                       "cloud_setup/setup_sql_proxy.sh" \
                       "cloud_setup/create_schema.sh"
