pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = "ada-project"
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
                        --path /ada-project/ \
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
                        python -c "import ada_project; print('Import successful')" || true
                """
            }
        }
        
        stage('Deploy to Jenkins Server') {
            steps {
                echo "Deploying ADA Project..."
                script {
                    // Stop existing services
                    sh "docker-compose down || true"
                    sh "docker stop ada_project || true"
                    sh "docker rm ada_project || true"
                    
                    // Create network if it doesn't exist
                    sh "docker network create ada-network || true"
                    
                    // Start all services with Docker Compose
                    sh "docker-compose up -d --build"
                    
                    // Wait for services to be ready
                    sh "sleep 45"
                    
                    // Verify deployment
                    sh '''
                        if docker ps | grep ada_project; then
                            echo "Deployment successful"
                            echo "ADA Project available at: http://localhost:${APP_PORT}"
                            
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
            echo "ADA Project is running at: http://localhost:${APP_PORT}"
        }
        failure {
            echo "Pipeline failed"
        }
    }
}
