app:
	gcloud app deploy

revoke:
	gcloud auth revoke heilbroner.lockbreaker@gmail.com

auth:
	gcloud config configurations activate personal
	gcloud auth login