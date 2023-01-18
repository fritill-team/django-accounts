"use strict";

var KTSignInGeneral = function () {
  var form,
      submitButton,
      validator;

  var setAuthenticationField = function () {

  }

  var handleForm = function (e) {
    validator = FormValidation.formValidation(
        form,
        {
          fields: {
            email: {
              validators: {
                regexp: {
                  regexp: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                  message: 'The value is not a valid email address',
                },
                notEmpty: {
                  message: 'Email address is required'
                }
              }
            },
            password: {
              validators: {
                notEmpty: {
                  message: 'The password is required'
                }
              }
            }
          },
          plugins: {
            trigger: new FormValidation.plugins.Trigger(),
            bootstrap: new FormValidation.plugins.Bootstrap5({
              rowSelector: '.fv-row',
              eleInvalidClass: '',  // comment to enable invalid state icons
              eleValidClass: '' // comment to enable valid state icons
            })
          }
        }
    );
    submitButton.addEventListener('click', function (e) {
      e.preventDefault();

      validator.validate().then(function (status) {
        if (status === 'Valid') {
          submitButton.setAttribute('data-kt-indicator', 'on');

          submitButton.disabled = true;

          setTimeout(function () {
            submitButton.removeAttribute('data-kt-indicator');
            submitButton.disabled = false;
            Swal.fire({
              text: "You have successfully logged in!",
              icon: "success",
              buttonsStyling: false,
              confirmButtonText: "Ok, got it!",
              customClass: {
                confirmButton: "btn btn-primary"
              }
            }).then(function (result) {
              if (result.isConfirmed) {
                form.querySelector('[name="email"]').value = "";
                form.querySelector('[name="password"]').value = "";
                var redirectUrl = form.getAttribute('data-kt-redirect-url');
                if (redirectUrl) {
                  location.href = redirectUrl;
                }
              }
            });
          }, 2000);
        } else {
          Swal.fire({
            text: "Sorry, looks like there are some errors detected, please try again.",
            icon: "error",
            buttonsStyling: false,
            confirmButtonText: "Ok, got it!",
            customClass: {
              confirmButton: "btn btn-primary"
            }
          });
        }
      });
    });
  }

  return {
    init: function () {
      form = document.querySelector('#kt_sign_in_form');
      submitButton = document.querySelector('#kt_sign_in_submit');

      handleForm();
    }
  };
}();

KTUtil.onDOMContentLoaded(function () {
  KTSignInGeneral.init();
});
