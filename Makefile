app:
	gcloud app deploy

revoke:
	gcloud auth revoke heilbroner.lockbreaker@gmail.com &
	gcloud config configurations activate default &
	gcloud auth login &
	. cloud_setup/clear_access.sh

prod_environment:
	gcloud config configurations activate personal
	gcloud auth login
	gcloud auth application-default login

dev_environment:
	gcloud config configurations activate test-lockbreaker
	gcloud auth login
	gcloud auth application-default login

setup:
	. cloud_setup/setup.sh
