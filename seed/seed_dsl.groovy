streamFileFromWorkspace("${RECIPE_LIST_FILE}").eachLine {

  def recipeName = it
  def emailRecipients = "\${DEFAULT_RECIPIENTS}"
  def emailSubject = "\${PROJECT_NAME} - \${BUILD_STATUS}"
  def emailBody = "\${BUILD_LOG}"

  job {
    name "${recipeName}"

    label('mavericks')

    multiscm {
      git('git://github.com/autopkg/autopkg.git', 'master')
    }

    triggers {
      cron('H H(0-7),H(8-15),H(16-23) * * *')
    }

    steps {
      shell("echo ${recipeName} > recipe.txt")
      shell(readFileFromWorkspace('autopkg-ci/steps/autopkg_run.py'))
    }

    publishers {
      extendedEmail(emailRecipients, emailSubject, emailBody) {
        trigger('Failure')
        trigger('Fixed')
        trigger(triggerName: 'StillFailing', subject: emailSubject, body:emailBody, recipientList:emailRecipients,
            sendToDevelopers: false, sendToRequester: false, includeCulprits: false, sendToRecipientList: false)
      }
    }

    configure { project ->
      project << logRotator {
          daysToKeep(60)
          numToKeep(-1)
          artifactDaysToKeep(-1)
          artifactNumToKeep(-1)
      }

      def setter = project / publishers / 'hudson.plugins.descriptionsetter.DescriptionSetterPublisher'
      setter / regexp << '^PARSED_VERSION (.*)'
      setter / regexpForFailed << ''
      setter / setForMatrix << 'false'
    }
  }
}
