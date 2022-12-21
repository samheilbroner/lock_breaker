app:
	gcloud app deploy

revoke:
	gcloud auth revoke heilbroner.lockbreaker@gmail.com
	gcloud config configurations activate default

auth:
	gcloud config configurations activate personal
	gcloud auth login