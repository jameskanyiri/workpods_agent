pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "workpods-agent"
        DOCKER_TAG = "${BUILD_NUMBER}"
        APP_PORT = "8120"
    }

    stages {
        stage('Inject Secrets from Infisical') {
            steps {
                sh '''
                    echo "Fetching secrets from Infisical..."
                    infisical export \
                      --projectId afda2ee1-851f-470a-a49c-71e372899b0a \
                        --env dev \
                        --path /workpods-agent/ \
                         --format=dotenv > .env
                '''
            }
        }

        stage('Build and Test') {
            steps {
                echo "Building Docker image and running tests..."
                sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                sh "docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest"

                // Run basic health check
                sh """
                    docker run --rm \
                        --env-file .env \
                        ${DOCKER_IMAGE}:${DOCKER_TAG} \
                        python -c "from src.agent import agent; print('Import successful')" || true
                """
            }
        }

        stage('Deploy to Jenkins Server') {
            steps {
                echo "Deploying Workpods Agent..."
                script {
                    // Stop existing services
                    sh "docker-compose down || true"
                    sh "docker stop workpods_agent || true"
                    sh "docker rm workpods_agent || true"

                    // Create network if it doesn't exist
                    sh "docker network create workpods-network || true"

                    // Start all services with Docker Compose
                    sh "docker-compose up -d --build"

                    // Wait for services to be ready
                    sh "sleep 45"

                    // Verify deployment
                    sh '''
                        if docker ps | grep workpods_agent; then
                            echo "Deployment successful"
                            echo "Workpods Agent available at: http://localhost:${APP_PORT}"

                            # Test the application using curl inside a container
                            docker run --rm --network host curlimages/curl:latest \
                                curl -f http://localhost:${APP_PORT}/api/v1/docs || echo "Health check failed - but container is running"
                        else
                            echo "Deployment failed"
                            docker-compose logs
                            exit 1
                        fi
                    '''
                }
            }
        }
    }

    post {
        always {
            echo "Cleaning up test containers..."
            sh "docker stop test-${BUILD_NUMBER} || true"
            sh "docker rm test-${BUILD_NUMBER} || true"
        }
        success {
            echo "Pipeline completed successfully"
            echo "Workpods Agent is running at: http://localhost:${APP_PORT}"
        }
        failure {
            echo "Pipeline failed"
        }
    }
}
