"use strict";

// Class Definition
var KTSigninTwoSteps = function () {
  // Elements
  var inputs,
    submitButton,
    codeInput,
    resendContainer,
    resendCounterInterval,
    i18n,
    DOM

  var initDOM = function () {
    DOM = {
      setCounter(seconds) {
        resendContainer.html($(`<span class="text-muted me-1">${i18n.resendCounter} ${seconds}</span>`))
      },
      setResendLink() {
        resendContainer.fadeOut(150, function () {
          $(this).empty()
          $(this).append($(`<span class="text-muted me-1">${i18n.resendText}</span>
             <a href="${$(this).data('resend-url')}"
                id="resend-verification-code"
                class="link-primary fs-5 me-1">${i18n.resendLinkText}</a>`)).fadeIn(150)
        })
      }
    }
  }

  var initLocalization = function () {
    i18n = {
      resendText: gettext("Didn’t get the code ?"),
      resendLinkText: gettext("Resend"),
      resendCounter: gettext('You can resend again in..')
    }
  }

  var resendCountDown = function () {
    var endTime = new Date(0)
    endTime.setSeconds(resendContainer.data('otp-expires-at'))

    if (endTime) {
      resendCounterInterval = setInterval(function () {
        var curTime = new Date(),
          seconds = Math.floor((endTime - curTime) / 1000)

        if (seconds <= 0) {
          clearInterval(resendCounterInterval)
          DOM.setResendLink()
        } else {
          DOM.setCounter(seconds)
        }
      }, 1000);
    } else
      resendContainer.fadeOut(50, function () {
        DOM.setResendLink(this)
      })
  }

  var updateSubmitButton = function () {
    var valuesList = []
    inputs.each(function (i, item) {
      if ($(item).val().length > 0)
        valuesList.push($(item).val())
    })

    codeInput.val(valuesList.join(''))

    if (valuesList.length === 6)
      submitButton.removeClass('disabled')
    else
      submitButton.addClass('disabled')
  }

  var handleType = function () {
    inputs[0].focus()

    inputs.each(function (i, item) {
      var $item = $(item),
        order = Number($item.data('otp-input')),
        next = order + 1,
        prev = order - 1,
        nextEl

      $item.on('keyup', function (e) {
        if ($item.val().length === 1 && (e.keyCode >= 45 && e.keyCode <= 57) || (e.keyCode >= 96 && e.keyCode <= 105)) {
          nextEl = $(`[data-otp-input=${next}]`)
          nextEl.focus()
          nextEl.select()
        }
        updateSubmitButton()
      })
      $item.on('keydown', function (e) {

        if (e.keyCode === 8) {
          if ($item.val().length === 0)
            $(`[data-otp-input=${prev}]`).focus().select()
        } else if (e.keyCode === 37)
          $(`[data-otp-input=${prev}]`).focus().select()
        else if (e.keyCode === 39)
          $(`[data-otp-input=${next}]`).focus().select()
      })
    })


  }

  var resendVerificationCode = function () {
    $(document).on('click', '#resend-verification-code', function (e) {
      e.preventDefault()

      $.ajax({
        url: $(this).attr('href'),
        success(response) {
          resendContainer.data('otp-expires-at', response['otp_expiry'])
          resendCountDown()
        }
      })
    })
  }

  return {
    init: function () {
      inputs = $('[data-otp-input]')
      submitButton = $('#form-submit')
      codeInput = $('#id_code')
      resendContainer = $('[data-otp-expires-at]')
      initLocalization()
      initDOM()
      handleType()
      resendCountDown()
      resendVerificationCode()
    }
  };
}();

// On document ready
KTUtil.onDOMContentLoaded(function () {
  KTSigninTwoSteps.init();
});