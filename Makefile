app:
	gcloud app deploy

revoke:
	gcloud auth revoke heilbroner.lockbreaker@gmail.com
	gcloud config configurations activate default
	. cloud_setup/clear_access.sh

prod_environment:
	gcloud config configurations activate personal
	gcloud auth login
	. cloud_setup/configure_environment_variables.sh

dev_environment:
	gcloud config configurations activate lockbreaker-test
	gcloud auth login
	. cloud_setup/configure_environment_variables.sh

setup:
	chmod +x ./cloud_setup/enable_postgres.sh ./cloud_setup/create_bq_dataset.sh ./cloud_setup/create_service_account.sh
	. cloud_setup/enable_bq.sh
	. cloud_setup/create_bq_dataset.sh
	. cloud_setup/create_service_account.sh