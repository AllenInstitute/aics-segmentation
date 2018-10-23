#!groovy

node ("python-gradle")
{
    // parameters { booleanParam(name: 'promote_artifact', defaultValue: false, description: '') }
    // def is_promote=(params.promote_artifact)
    // echo "BUILDTYPE: " + (is_promote ? "Promote Image" : "Build, Publish and Tag")
    parameters { booleanParam(name: 'create_release', defaultValue: false, 
                              description: 'If true, create a release artifact and publish to ' +
                                           'the artifactory release PyPi or public PyPi.') }
    def create_release=(params.create_release)
    echo "BUILDTYPE: " + (create_release ? "Creating a Release" : "Building a Snapshot")

    try {
        stage ("git pull") {
            def git_url=gitUrl()
            if (env.BRANCH_NAME == null) {
                git url: "${git_url}"
            }
            else {
                println "*** BRANCH ${env.BRANCH_NAME}"
                git url: "${git_url}", branch: "${env.BRANCH_NAME}"
            }
        }

        stage ("initialize virtualenv") {
            sh "./gradlew -i cleanAll installCIDependencies"
        }

        stage ("bump version pre-build") {
            // This will drop the dev suffix if we are releasing
            if (create_release) {
                // X.Y.Z.devN -> X.Y.Z
                sh "./gradlew -i bumpVersionRelease"
            }
        }

        stage ("test/build distribution") {
            sh './gradlew -i build'
        }

        junit "build/test_report.xml"

        stage ("publish") {
            def publish_task = create_release ? "publishRelease" : "publishSnapshot"
            sh "./gradlew -i ${publish_task}"
        }

        stage ("tag release") {
            if (create_release) {
                sh "./gradlew -i gitTagCommitPush"
            }
        }

        stage ("prep for dev") {
            // if after release build: X.Y.Z -> X.Y.Z+1.dev0  (patch)
            // if snapshot build: X.Y.Z.devN -> X.Y.Z.devN+1  (devbuild)
            def bumpTask = create_release ? "bumpVersionPostRelease" : "bumpVersionDev"
            sh "./gradlew -i ${bumpTask}"
            sh "./gradlew -i gitCommitPush"
        }

        currentBuild.result = "SUCCESS"
    }
    catch(e) {
        // If there was an exception thrown, the build failed
        currentBuild.result = "FAILURE"
        throw e
    }
    finally {

        if (currentBuild?.result) {
            println "BUILD: ${currentBuild.result}"
        }
        // Slack
        notifyBuildOnSlack(currentBuild.result, currentBuild.previousBuild?.result)

        // Email
        step([$class: 'Mailer',
              notifyEveryUnstableBuild: true,
              recipients: '!AICS_DevOps@alleninstitute.org',
              sendToIndividuals: true])
    }
}

def gitUrl() {
    checkout scm
    sh(returnStdout: true, script: 'git config remote.origin.url').trim()
}

def notifyBuildOnSlack(String buildStatus = 'STARTED', String priorStatus) {
    // build status of null means successful
    buildStatus =  buildStatus ?: 'SUCCESS'

    // Override default values based on build status
    if (buildStatus != 'SUCCESS') {
        slackSend (
                color: '#FF0000',
                message: "${buildStatus}: '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})"
        )
    } else if (priorStatus != 'SUCCESS') {
        slackSend (
                color: '#00FF00',
                message: "BACK_TO_NORMAL: '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})"
        )
    }
}
