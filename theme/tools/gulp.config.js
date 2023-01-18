const gulpConfig = {
  name: 'Django Accounts',
  desc: "Gulp build config",
  version: "8.1.6",
  config: {
    debug: false,
    compile: {
      rtl: {
        enabled: true,
        skip: [
          "select2",
          "sweetalert2",
        ],
      },
      jsMinify: false,
      cssMinify: false,
      jsSourcemaps: false,
      cssSourcemaps: false,
    },
    path: {
      src: "../{demo}/src",
      common_src: "../{demo}/src",
      node_modules: "node_modules",
    },
    dist: ["../{demo}/dist/assets"],
  },
  build: {
    base: {
      src: {
        styles: ["{$config.path.src}/sass/style.scss"],
        scripts: [
          "{$config.path.common_src}/js/components/**/*.js",
          "{$config.path.common_src}/js/layout/**/*.js",
          "{$config.path.src}/js/layout/**/*.js"
        ]
      },
      dist: {
        styles: "{$config.dist}/css/style.bundle.css",
        scripts: "{$config.dist}/js/scripts.bundle.js",
      }
    },
    plugins: {
      global: {
        src: {
          mandatory: {
            jquery: {
              scripts: ["{$config.path.node_modules}/jquery/dist/jquery.js"],
            },
            popperjs: {
              scripts: [
                "{$config.path.node_modules}/@popperjs/core/dist/umd/popper.js",
              ],
            },
            bootstrap: {
              scripts: [
                "{$config.path.node_modules}/bootstrap/dist/js/bootstrap.min.js",
              ],
            },
            moment: {
              scripts: [
                "{$config.path.node_modules}/moment/min/moment-with-locales.min.js",
              ],
            },
            wnumb: {
              scripts: ["{$config.path.node_modules}/wnumb/wNumb.js"],
            },
          },
          optional: {
            select2: {
              styles: [
                "{$config.path.node_modules}/select2/dist/css/select2.css",
              ],
              scripts: [
                "{$config.path.node_modules}/select2/dist/js/select2.full.js",
                "{$config.path.common_src}/js/vendors/plugins/select2.init.js",
              ],
            },
            flatpickr: {
              styles: [
                "{$config.path.node_modules}/flatpickr/dist/flatpickr.css",
              ],
              scripts: [
                "{$config.path.node_modules}/flatpickr/dist/flatpickr.js"
              ],
            },
            formvalidation: {
              styles: [
                "{$config.path.common_src}/plugins/formvalidation/dist/css/formValidation.css",
              ],
              scripts: [
                "{$config.path.node_modules}/es6-shim/es6-shim.js",
                "{$config.path.common_src}/plugins/formvalidation/dist/js/FormValidation.full.min.js",
                "{$config.path.common_src}/plugins/formvalidation/dist/js/plugins/Bootstrap5.min.js"
              ],
            },
            daterangepicker: {
              styles: [
                "{$config.path.node_modules}/bootstrap-daterangepicker/daterangepicker.css",
              ],
              scripts: [
                "{$config.path.node_modules}/bootstrap-daterangepicker/daterangepicker.js",
              ],
            },
            inputmask: {
              scripts: [
                "{$config.path.node_modules}/inputmask/dist/inputmask.js",
                "{$config.path.node_modules}/inputmask/dist/bindings/inputmask.binding.js"
              ]
            },
            smoothscroll: {
              scripts: [
                "{$config.path.node_modules}/smooth-scroll/dist/smooth-scroll.js",
              ],
            },
            toastr: {
              styles: ["{$config.path.common_src}/plugins/toastr/build/toastr.css"],
              scripts: ["{$config.path.common_src}/plugins/toastr/build/toastr.min.js"],
            },
            sweetalert2: {
              styles: [
                "{$config.path.node_modules}/sweetalert2/dist/sweetalert2.css",
              ],
              scripts: [
                "{$config.path.node_modules}/es6-promise-polyfill/promise.min.js",
                "{$config.path.node_modules}/sweetalert2/dist/sweetalert2.min.js",
                "{$config.path.common_src}/js/vendors/plugins/sweetalert2.init.js",
              ],
            },
          },
          override: {
            styles: ["{$config.path.src}/sass/plugins.scss"],
          },
        },
        dist: {
          styles: "{$config.dist}/plugins/global/plugins.bundle.css",
          scripts: "{$config.dist}/plugins/global/plugins.bundle.js",
          images: "{$config.dist}/plugins/global/images",
          fonts: "{$config.dist}/plugins/global/fonts",
        },
      },
      custom: {}
    },
    widgets: {
      src: {
        scripts: [
          "{$config.path.common_src}/js/widgets/**/*.js"
        ]
      },
      dist: {
        scripts: "{$config.dist}/js/widgets.bundle.js",
      }
    },
    custom: {
      src: {
        styles: [
          "{$config.path.common_src}/sass/custom/**/*.scss",
          "{$config.path.src}/sass/custom/**/*.scss",
        ],
        scripts: [
          "{$config.path.common_src}/js/custom/**/*.js",
          "{$config.path.src}/js/custom/**/*.js",
        ],
      },
      dist: {
        styles: "{$config.dist}/css/custom/",
        scripts: "{$config.dist}/js/custom/",
      },
    },
    media: {
      src: {
        media: [
          "{$config.path.common_src}/media/**/*.*",
          "{$config.path.src}/media/**/*.*",
        ],
      },
      dist: {
        media: "{$config.dist}/media/",
      },
    },
    /*misc: {
      src: {
        styles: [
          "{$config.path.node_modules}/tinymce/skins/!**!/!*.css"
        ],
        media: [
          "{$config.path.node_modules}/tiny-slider/dist/sourcemaps/tiny-slider.css.map",
        ],
      },
      dist: {
        styles: "{$config.dist}/plugins/custom/tinymce/skins/",
        media: "{$config.dist}/plugins/global/sourcemaps/",
      }
    }*/
  }
};

export {
  gulpConfig
};