app:
	gcloud app deploy

revoke:
	gcloud auth revoke heilbroner.lockbreaker@gmail.com
	gcloud config configurations activate default
	. cloud_setup/clear_access.sh

prod_environment:
	gcloud config configurations activate personal
	gcloud auth login

dev_environment:
	gcloud config configurations activate lockbreaker-test
	gcloud auth login

setup:
	. cloud_setup/setup.sh