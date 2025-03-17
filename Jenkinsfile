pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                script {
                    dir("${params.project}") {
                        bat "git fetch"
                        bat "git pull"
                    }
                }
            }
        }
        stage('Tests') {
            steps {
                script {
                    def tasks = ['Task4', 'Task5']
                    tasks.each { task ->
                        stage("Test: ${task}") {
                            catchError(stageResult: 'FAILURE') {
                                bat "${params.runner} account-book ${task}"
                            }
                        }
                    }
                }
            }
        }
    }
}