window["kvideocomp"] =
/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, { enumerable: true, get: getter });
/******/ 		}
/******/ 	};
/******/
/******/ 	// define __esModule on exports
/******/ 	__webpack_require__.r = function(exports) {
/******/ 		if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 			Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 		}
/******/ 		Object.defineProperty(exports, '__esModule', { value: true });
/******/ 	};
/******/
/******/ 	// create a fake namespace object
/******/ 	// mode & 1: value is a module id, require it
/******/ 	// mode & 2: merge all properties of value into the ns
/******/ 	// mode & 4: return value when already ns object
/******/ 	// mode & 8|1: behave like require
/******/ 	__webpack_require__.t = function(value, mode) {
/******/ 		if(mode & 1) value = __webpack_require__(value);
/******/ 		if(mode & 8) return value;
/******/ 		if((mode & 4) && typeof value === 'object' && value && value.__esModule) return value;
/******/ 		var ns = Object.create(null);
/******/ 		__webpack_require__.r(ns);
/******/ 		Object.defineProperty(ns, 'default', { enumerable: true, value: value });
/******/ 		if(mode & 2 && typeof value != 'string') for(var key in value) __webpack_require__.d(ns, key, function(key) { return value[key]; }.bind(null, key));
/******/ 		return ns;
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";
/******/
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(__webpack_require__.s = "./src/lib/index.js");
/******/ })
/************************************************************************/
/******/ ({

/***/ "./src/lib/components/KvideoComp.react.js":
/*!************************************************!*\
  !*** ./src/lib/components/KvideoComp.react.js ***!
  \************************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "default", function() { return KvideoComp; });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var prop_types__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! prop-types */ "prop-types");
/* harmony import */ var prop_types__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(prop_types__WEBPACK_IMPORTED_MODULE_1__);
function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); return Constructor; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) _setPrototypeOf(subClass, superClass); }

function _setPrototypeOf(o, p) { _setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return _setPrototypeOf(o, p); }

function _createSuper(Derived) { var hasNativeReflectConstruct = _isNativeReflectConstruct(); return function _createSuperInternal() { var Super = _getPrototypeOf(Derived), result; if (hasNativeReflectConstruct) { var NewTarget = _getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return _possibleConstructorReturn(this, result); }; }

function _possibleConstructorReturn(self, call) { if (call && (_typeof(call) === "object" || typeof call === "function")) { return call; } return _assertThisInitialized(self); }

function _assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function _isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function _getPrototypeOf(o) { _getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return _getPrototypeOf(o); }



/**
 * ExampleComponent is an example component.
 * It takes a property, `label`, and
 * displays it.
 * It renders an input with the property `value`
 * which is editable by the user.
 */

var KvideoComp = /*#__PURE__*/function (_Component) {
  _inherits(KvideoComp, _Component);

  var _super = _createSuper(KvideoComp);

  function KvideoComp(props) {
    var _this;

    _classCallCheck(this, KvideoComp);

    _this = _super.call(this, props);
    _this.pc = null;
    _this.clickCount = 0;
    return _this;
  }

  _createClass(KvideoComp, [{
    key: "negotiate",
    value: function negotiate() {
      var pc = this.pc;
      pc.addTransceiver('video', {
        direction: 'recvonly'
      });
      return pc.createOffer().then(function (offer) {
        return pc.setLocalDescription(offer);
      }).then(function () {
        // wait for ICE gathering to complete
        return new Promise(function (resolve) {
          if (pc.iceGatheringState === 'complete') {
            resolve();
          } else {
            var checkState = function checkState() {
              if (pc.iceGatheringState === 'complete') {
                pc.removeEventListener('icegatheringstatechange', checkState);
                resolve();
              }
            };

            pc.addEventListener('icegatheringstatechange', checkState);
          }
        });
      }).then(function () {
        var offer = pc.localDescription;
        return fetch('offer', {
          body: JSON.stringify({
            sdp: offer.sdp,
            type: offer.type
          }),
          headers: {
            'Content-Type': 'application/json'
          },
          method: 'POST'
        });
      }).then(function (response) {
        return response.json();
      }).then(function (answer) {
        return pc.setRemoteDescription(answer);
      });
    }
  }, {
    key: "start",
    value: function start() {
      var id = this.props.id;
      var config = {
        sdpSemantics: 'unified-plan'
      };
      config.iceServers = [{
        urls: ['stun:stun.l.google.com:19302']
      }];
      this.pc = new RTCPeerConnection(config); // connect video

      this.pc.addEventListener('track', function (evt) {
        if (evt.track.kind == 'video') {
          document.getElementById(id).srcObject = evt.streams[0];
        }
      });
      this.negotiate();
    }
  }, {
    key: "stop",
    value: function stop() {
      if (this.pc !== null) this.pc.close();
    }
  }, {
    key: "componentDidMount",
    value: function componentDidMount() {
      var _this2 = this;

      var _this$props = this.props,
          id = _this$props.id,
          overlay_id = _this$props.overlay_id;
      var video = document.getElementById(id);

      var handlePointer = function handlePointer(e) {
        if (e.button == 0) {
          var _this2$props = _this2.props,
              source_width = _this2$props.source_width,
              source_height = _this2$props.source_height;
          var x = Math.floor(e.offsetX / video.clientWidth * source_width);
          var y = Math.floor(e.offsetY / video.clientHeight * source_height);

          _this2.props.setProps({
            click_data: [_this2.clickCount, x, y]
          });

          _this2.clickCount++;
        }
      };

      var handleTimer = function handleTimer() {
        var figure = document.getElementById(overlay_id);
        var nsew = document.getElementsByClassName("nsewdrag")[0];
        if (figure) figure.addEventListener("pointerdown", handlePointer); // Change cursor to crosshair for nsewdrag

        if (nsew) nsew.style.cursor = "crosshair";
      };

      video.addEventListener("pointerdown", handlePointer); // We need to wait a bit for page initialization before we can add event listener, etc.

      setTimeout(handleTimer, 1000);
      this.start();
    }
  }, {
    key: "componentWillUnmount",
    value: function componentWillUnmount() {
      this.stop();
    }
  }, {
    key: "render",
    value: function render() {
      var _this$props2 = this.props,
          id = _this$props2.id,
          style = _this$props2.style;
      return /*#__PURE__*/react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement("video", {
        id: id,
        autoPlay: true,
        playsInline: true,
        muted: true,
        style: style
      });
    }
  }]);

  return KvideoComp;
}(react__WEBPACK_IMPORTED_MODULE_0__["Component"]);


KvideoComp.defaultProps = {};
KvideoComp.propTypes = {
  /**
   * The ID used to identify this component in Dash callbacks.
   */
  id: prop_types__WEBPACK_IMPORTED_MODULE_1___default.a.string,

  /**
   * The ID used to identify an overlay component that we register mouse events.
   */
  overlay_id: prop_types__WEBPACK_IMPORTED_MODULE_1___default.a.string,

  /**
   * click_data 
   */
  click_data: prop_types__WEBPACK_IMPORTED_MODULE_1___default.a.array,

  /**
   * source width, hint for click callback.
   */
  source_width: prop_types__WEBPACK_IMPORTED_MODULE_1___default.a.number,

  /**
   * source height, hint for click callback.
   */
  source_height: prop_types__WEBPACK_IMPORTED_MODULE_1___default.a.number,

  /**
   * style is used to pass style parameters to video component.
   */
  style: prop_types__WEBPACK_IMPORTED_MODULE_1___default.a.string,

  /**
   * Dash-assigned callback that should be called to report property changes
   * to Dash, to make them available for callbacks.
   */
  setProps: prop_types__WEBPACK_IMPORTED_MODULE_1___default.a.func
};

/***/ }),

/***/ "./src/lib/index.js":
/*!**************************!*\
  !*** ./src/lib/index.js ***!
  \**************************/
/*! exports provided: KvideoComp */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _components_KvideoComp_react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./components/KvideoComp.react */ "./src/lib/components/KvideoComp.react.js");
/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, "KvideoComp", function() { return _components_KvideoComp_react__WEBPACK_IMPORTED_MODULE_0__["default"]; });

/* eslint-disable import/prefer-default-export */



/***/ }),

/***/ "prop-types":
/*!****************************!*\
  !*** external "PropTypes" ***!
  \****************************/
/*! no static exports found */
/***/ (function(module, exports) {

(function() { module.exports = window["PropTypes"]; }());

/***/ }),

/***/ "react":
/*!************************!*\
  !*** external "React" ***!
  \************************/
/*! no static exports found */
/***/ (function(module, exports) {

(function() { module.exports = window["React"]; }());

/***/ })

/******/ });
//# sourceMappingURL=kvideocomp.dev.js.map