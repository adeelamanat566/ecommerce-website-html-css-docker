
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

        stage('DEPLOY DEV') {
            steps {
                sh '''
                    export TAG=${TAG}
                    docker compose up -d --build
                    docker ps -a
                '''
            }
        }

        stage('TEST DEV') {
            steps {
                sh '''
                    echo "Testing DEV deployment..."
                    docker ps
                '''
            }
        }

        stage('APPROVE LIVE') {
            steps {
                input message: 'DEV tested successfully. Deploy to LIVE?', ok: 'Deploy LIVE'
            }
        }

        stage('DEPLOY LIVE') {
            steps {
                sshagent(['live-server']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no ubuntu@15.252.146.239 "
                            cd /home/ubuntu/app &&
                            export TAG=${TAG} &&
                            docker compose pull &&
                            docker compose up -d &&
                            docker ps
                        "
                    '''
                }
            }
        }
    }
}
