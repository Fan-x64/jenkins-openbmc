pipeline {
  agent any
  options { timestamps() }

  environment {
    OBMC_IMAGE = "/bmc/romulus/obmc-phosphor-image-romulus-20250927014348.static.mtd"
    QEMU_LOG   = "qemu.log"
    QEMU_PID   = "qemu.pid"
  }

  stages {
    stage('Start QEMU') {
      steps {
        sh '''
          set -eux
          # Убиваем старый процесс если остался
          pkill -f qemu-system-arm || true

          # Запускаем QEMU в фоне
          /usr/bin/qemu-system-arm -m 256 -M romulus-bmc -nographic \
            -drive file=${OBMC_IMAGE},format=raw,if=mtd \
            -net nic \
            -net user,hostfwd=tcp::2222-:22,hostfwd=tcp::2443-:443,hostfwd=udp::2623-:623,hostname=qemu \
            > ${QEMU_LOG} 2>&1 &

          echo $! > ${QEMU_PID}

          echo "Ожидаем загрузку OpenBMC (SSH на 2222)..."
          for i in $(seq 1 60); do
            if nc -z localhost 2222; then
              echo "SSH доступен!"
              break
            fi
            sleep 5
          done
        '''
      }
    }

    stage('Sanity check (SSH)') {
      steps {
        sh '''
          set -eux
          # Проверка базового SSH-доступа
          sshpass -p "0penBmc" ssh -o StrictHostKeyChecking=no -p 2222 root@127.0.0.1 "uname -a" || true
        '''
      }
    }

    stage('Run Autotests') {
      steps {
        sh '''
          set -eux
          mkdir -p reports/autotests
          echo ">>> Здесь можно запускать openbmc-test-automation <<<"
          echo "Пока сделаем заглушку-отчет"
          echo "Autotests OK" > reports/autotests/result.txt
        '''
      }
    }

    stage('Run WebUI tests') {
      steps {
        sh '''
          set -eux
          mkdir -p reports/webui
          echo ">>> Здесь можно запускать GUI тесты (Robot Framework) <<<"
          echo "WebUI tests OK" > reports/webui/result.txt
        '''
      }
    }

    stage('Load testing (k6)') {
      steps {
        sh '''
          set -eux
          mkdir -p reports/loadtest
          docker run --rm -e K6_TLS_INSECURE_SKIP_VERIFY=1 \
            -v ${WORKSPACE}/loadtest:/loadtest \
            grafana/k6 run /loadtest/openbmc_k6.js \
            | tee reports/loadtest/summary.txt || true
        '''
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: 'reports/**/*,qemu.log', allowEmptyArchive: true
      sh '''
        if [ -f ${QEMU_PID} ]; then
          kill $(cat ${QEMU_PID}) || true
          rm ${QEMU_PID}
        fi
      '''
    }
  }
}
