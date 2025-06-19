pipeline {
  agent any

  environment {
    DEPLOY_USER = 'mlops'
    DEPLOY_HOST = '192.168.28.38'
    REMOTE_DIR = '/home/mlops/chat-app'
    COMPOSE_FILE = 'infrastructure/dockercompose.yml'
  }

  stages {

    stage('Lấy mã nguồn từ GitHub') {
      steps {
        checkout scm
      }
      post {
        failure {
          emailext(
            subject: "❌ FAILED: Checkout stage in ${env.JOB_NAME} #${env.BUILD_NUMBER}",
            body: """<p>Stage <b>Checkout</b> failed in <b>${env.JOB_NAME}</b> build #${env.BUILD_NUMBER}.</p>
                     <p><a href="${env.BUILD_URL}">${env.BUILD_URL}</a></p>""",
            to: 'khanh2003dakdoa@gmail.com'
          )
        }
      }
    }

    stage('Tạo thư mục nếu chưa có') {
      steps {
        script {
          sshagent(['deploy-key']) {
            sh """
              ssh -o StrictHostKeyChecking=no ${DEPLOY_USER}@${DEPLOY_HOST} '
                mkdir -p ${REMOTE_DIR}
              '
            """
          }
        }
      }
      post {
        failure {
          emailext(
            subject: "❌ FAILED: Prepare directory stage in ${env.JOB_NAME} #${env.BUILD_NUMBER}",
            body: """<p>Stage <b>Prepare Directory</b> failed in build #${env.BUILD_NUMBER}.</p>
                     <p><a href="${env.BUILD_URL}">${env.BUILD_URL}</a></p>""",
            to: 'khanh2003dakdoa@gmail.com'
          )
        }
      }
    }

    stage('Sao chép mã nguồn bằng SCP') {
      steps {
        script {
          sshagent(['deploy-key']) {
            sh """
              echo "🗂️ Xoá nội dung cũ trên server..."
              ssh ${DEPLOY_USER}@${DEPLOY_HOST} 'rm -rf ${REMOTE_DIR}/*'

              echo "📤 Copy toàn bộ project lên server..."
              scp -r . ${DEPLOY_USER}@${DEPLOY_HOST}:${REMOTE_DIR}/
            """
          }
        }
      }
      post {
        failure {
          emailext(
            subject: "❌ FAILED: Upload code (SCP) stage in ${env.JOB_NAME} #${env.BUILD_NUMBER}",
            body: """<p>Stage <b>Upload Code</b> failed in build #${env.BUILD_NUMBER}.</p>
                     <p><a href="${env.BUILD_URL}">${env.BUILD_URL}</a></p>""",
            to: 'khanh2003dakdoa@gmail.com'
          )
        }
      }
    }

    stage('Tạo volume và network nếu chưa có') {
      steps {
        script {
          sshagent(['deploy-key']) {
            sh """
              ssh ${DEPLOY_USER}@${DEPLOY_HOST} '
                docker volume create fastapi-logs || true &&
                docker network create prom || true
              '
            """
          }
        }
      }
      post {
        failure {
          emailext(
            subject: "❌ FAILED: Create volume/network stage in ${env.JOB_NAME} #${env.BUILD_NUMBER}",
            body: """<p>Stage <b>Create Volume/Network</b> failed in build #${env.BUILD_NUMBER}.</p>
                     <p><a href="${env.BUILD_URL}">${env.BUILD_URL}</a></p>""",
            to: 'khanh2003dakdoa@gmail.com'
          )
        }
      }
    }

    stage('Triển khai với Docker Compose') {
      steps {
        script {
          sshagent(['deploy-key']) {
            sh """
              ssh ${DEPLOY_USER}@${DEPLOY_HOST} '
                cd ${REMOTE_DIR} &&
                docker-compose -f ${COMPOSE_FILE} down &&
                docker-compose -f ${COMPOSE_FILE} up -d --build
              '
            """
          }
        }
      }
      post {
        failure {
          emailext(
            subject: "❌ FAILED: Deploy stage in ${env.JOB_NAME} #${env.BUILD_NUMBER}",
            body: """<p>Stage <b>Deploy with Docker Compose</b> failed in build #${env.BUILD_NUMBER}.</p>
                     <p><a href="${env.BUILD_URL}">${env.BUILD_URL}</a></p>""",
            to: 'khanh2003dakdoa@gmail.com'
          )
        }
      }
    }

  }
}
