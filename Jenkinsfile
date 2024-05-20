pipeline {
    agent any

    environment {
        VENV_DIR = '.venv'
        GDRIVE_CREDENTIALS_DATA = credentials('dvc_gdrive_creds')
        DOCKERHUB_CREDENTIALS = credentials('dockerhub_id')
        DOCKERHUB_REPO = 'urfunl2325/mlops-final-proj'  // Replace with your Docker Hub repository
    }

    stages {
        stage('Clone Git Repo') {
            steps {
                git url: 'https://github.com/mlteamurfu2325/mlops-final-proj.git', branch: 'main'
            }
        }

        stage('Get Commit SHA') {
            steps {
                script {
                    // Get the short SHA of the latest commit
                    IMAGE_TAG = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                }
            }
        }

        stage('Setup Python Virtual Environment') {
            steps {
                script {
                    // Create virtual environment
                    sh "python3 -m venv ${VENV_DIR}"
                }
            }
        }

        stage('Install Requirements') {
            steps {
                script {
                    // Activate virtual environment and install requirements
                    sh """
                        . ${VENV_DIR}/bin/activate
                        pip install -r requirements.txt
                    """
                }
            }
        }

        stage('DVC data and models pull') {
            steps {
                script {
                    // Activate virtual environment and pull DVC data and models
                    sh """
                        . ${VENV_DIR}/bin/activate
                        dvc pull
                    """
                }
            }
        }

        stage('Test Data Quality') {
            steps {
                script {
                    // Activate virtual environment and run data quality tests
                    sh '. ${VENV_DIR}/bin/activate && export PYTHONPATH=$(pwd) && pytest tests/test_data_quality.py'
                }
            }
        }

        stage('Test FastAPI endpoint') {
            steps {
                script {
                    // Activate virtual environment and run FastAPI endpoint tests
                    sh '. ${VENV_DIR}/bin/activate && export PYTHONPATH=$(pwd) && pytest tests/test_review_predict.py'
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${DOCKERHUB_REPO}:${IMAGE_TAG}")
                }
            }
        }

        stage('Push Docker Image to Docker Hub') {
            steps {
                script {
                    docker.withRegistry('', 'dockerhub_id') {
                        docker.image("${DOCKERHUB_REPO}:${IMAGE_TAG}").push()
                    }
                }
            }
        }

        stage('Debug Dir List') {
            steps {
                script {
                    // Echo directory structure
                    sh 'ls -R'
                }
            }
        }
    }

    post {
        always {
            // Clean up the virtual environment and workspace
            deleteDir()
        }
    }
}
