pipeline {
    agent any

    environment {
        IMAGE = 'adeelamanat56/night'
        TAG = "${BUILD_ID}"
    }

    stages {

        stage('CHECKOUT') {
            steps {
                checkout scm
            }
        }

        stage('BUILD') {
            steps {
                sh 'docker build -t ${IMAGE}:${TAG} .'
            }
        }

        stage('PUSH IMAGE') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )
                ]) {
                    sh '''
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker push ${IMAGE}:${TAG}
                        docker logout
                    '''
                }
            }
        }

        stage('DEPLOY') {
            steps {
                sh '''
                    export TAG=${TAG}
                    docker compose up -d
                    docker ps -a
                '''
            }
        }
    }
}