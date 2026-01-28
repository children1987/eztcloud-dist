"use strict";
/*
 * ATTENTION: The "eval" devtool has been used (maybe by default in mode: "development").
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
(self["webpackChunkmy_project"] = self["webpackChunkmy_project"] || []).push([["src_views_scene_detail_vue"],{

/***/ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/@vue/vue-loader-v15/lib/index.js??vue-loader-options!./src/views/scene/detail.vue?vue&type=script&lang=js":
/*!**************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/@vue/vue-loader-v15/lib/index.js??vue-loader-options!./src/views/scene/detail.vue?vue&type=script&lang=js ***!
  \**************************************************************************************************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

eval("{__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var vuex__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! vuex */ \"./node_modules/vuex/dist/vuex.esm.js\");\n/* provided dependency */ var console = __webpack_require__(/*! ./node_modules/console-browserify/index.js */ \"./node_modules/console-browserify/index.js\");\n\n/* harmony default export */ __webpack_exports__[\"default\"] = ({\n  computed: {\n    ...(0,vuex__WEBPACK_IMPORTED_MODULE_0__.mapState)({\n      currentProject: state => state.currentProject\n    }),\n    redURL() {\n      // return this.baseRedURL + `#flow/${this.currentProject.id}/`\n      return this.baseRedURL + `#flow/120c86e0b533db62/`;\n    }\n  },\n  data() {\n    return {\n      baseRedURL: \"http://192.168.1.11:1880/\"\n    };\n  },\n  created() {},\n  mounted() {\n    console.log(this.$refs.redframe);\n    this.$refs.redframe.onload = () => {\n      this.$refs.redframe.contentWindow.postMessage({\n        origin: 'red',\n        project: this.currentProject\n      }, '*');\n    };\n  }\n});\n\n//# sourceURL=webpack://my_project/./src/views/scene/detail.vue?./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use%5B0%5D!./node_modules/@vue/vue-loader-v15/lib/index.js??vue-loader-options\n}");

/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/@vue/vue-loader-v15/lib/loaders/templateLoader.js??ruleSet[1].rules[3]!./node_modules/@vue/vue-loader-v15/lib/index.js??vue-loader-options!./src/views/scene/detail.vue?vue&type=template&id=6ae34364":
/*!**********************************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/@vue/vue-loader-v15/lib/loaders/templateLoader.js??ruleSet[1].rules[3]!./node_modules/@vue/vue-loader-v15/lib/index.js??vue-loader-options!./src/views/scene/detail.vue?vue&type=template&id=6ae34364 ***!
  \**********************************************************************************************************************************************************************************************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

eval("{__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   render: function() { return /* binding */ render; },\n/* harmony export */   staticRenderFns: function() { return /* binding */ staticRenderFns; }\n/* harmony export */ });\nvar render = function render() {\n  var _vm = this,\n    _c = _vm._self._c;\n  return _c(\"iframe\", {\n    ref: \"redframe\",\n    attrs: {\n      src: _vm.redURL,\n      frameborder: \"0\",\n      height: \"100%\",\n      width: \"100%\"\n    }\n  });\n};\nvar staticRenderFns = [];\nrender._withStripped = true;\n\n\n//# sourceURL=webpack://my_project/./src/views/scene/detail.vue?./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use%5B0%5D!./node_modules/@vue/vue-loader-v15/lib/loaders/templateLoader.js??ruleSet%5B1%5D.rules%5B3%5D!./node_modules/@vue/vue-loader-v15/lib/index.js??vue-loader-options\n}");

/***/ }),

/***/ "./src/views/scene/detail.vue":
/*!************************************!*\
  !*** ./src/views/scene/detail.vue ***!
  \************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

eval("{__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _detail_vue_vue_type_template_id_6ae34364__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./detail.vue?vue&type=template&id=6ae34364 */ \"./src/views/scene/detail.vue?vue&type=template&id=6ae34364\");\n/* harmony import */ var _detail_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./detail.vue?vue&type=script&lang=js */ \"./src/views/scene/detail.vue?vue&type=script&lang=js\");\n/* harmony import */ var _node_modules_vue_vue_loader_v15_lib_runtime_componentNormalizer_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! !../../../node_modules/@vue/vue-loader-v15/lib/runtime/componentNormalizer.js */ \"./node_modules/@vue/vue-loader-v15/lib/runtime/componentNormalizer.js\");\n\n\n\n\n\n/* normalize component */\n;\nvar component = (0,_node_modules_vue_vue_loader_v15_lib_runtime_componentNormalizer_js__WEBPACK_IMPORTED_MODULE_2__[\"default\"])(\n  _detail_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__[\"default\"],\n  _detail_vue_vue_type_template_id_6ae34364__WEBPACK_IMPORTED_MODULE_0__.render,\n  _detail_vue_vue_type_template_id_6ae34364__WEBPACK_IMPORTED_MODULE_0__.staticRenderFns,\n  false,\n  null,\n  null,\n  null\n  \n)\n\n/* hot reload */\nif (false) // removed by dead control flow\n{ var api; }\ncomponent.options.__file = \"src/views/scene/detail.vue\"\n/* harmony default export */ __webpack_exports__[\"default\"] = (component.exports);\n\n//# sourceURL=webpack://my_project/./src/views/scene/detail.vue?\n}");

/***/ }),

/***/ "./src/views/scene/detail.vue?vue&type=script&lang=js":
/*!************************************************************!*\
  !*** ./src/views/scene/detail.vue?vue&type=script&lang=js ***!
  \************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

eval("{__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _node_modules_babel_loader_lib_index_js_clonedRuleSet_40_use_0_node_modules_vue_vue_loader_v15_lib_index_js_vue_loader_options_detail_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../../node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!../../../node_modules/@vue/vue-loader-v15/lib/index.js??vue-loader-options!./detail.vue?vue&type=script&lang=js */ \"./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/@vue/vue-loader-v15/lib/index.js??vue-loader-options!./src/views/scene/detail.vue?vue&type=script&lang=js\");\n /* harmony default export */ __webpack_exports__[\"default\"] = (_node_modules_babel_loader_lib_index_js_clonedRuleSet_40_use_0_node_modules_vue_vue_loader_v15_lib_index_js_vue_loader_options_detail_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__[\"default\"]); \n\n//# sourceURL=webpack://my_project/./src/views/scene/detail.vue?\n}");

/***/ }),

/***/ "./src/views/scene/detail.vue?vue&type=template&id=6ae34364":
/*!******************************************************************!*\
  !*** ./src/views/scene/detail.vue?vue&type=template&id=6ae34364 ***!
  \******************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

eval("{__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   render: function() { return /* reexport safe */ _node_modules_babel_loader_lib_index_js_clonedRuleSet_40_use_0_node_modules_vue_vue_loader_v15_lib_loaders_templateLoader_js_ruleSet_1_rules_3_node_modules_vue_vue_loader_v15_lib_index_js_vue_loader_options_detail_vue_vue_type_template_id_6ae34364__WEBPACK_IMPORTED_MODULE_0__.render; },\n/* harmony export */   staticRenderFns: function() { return /* reexport safe */ _node_modules_babel_loader_lib_index_js_clonedRuleSet_40_use_0_node_modules_vue_vue_loader_v15_lib_loaders_templateLoader_js_ruleSet_1_rules_3_node_modules_vue_vue_loader_v15_lib_index_js_vue_loader_options_detail_vue_vue_type_template_id_6ae34364__WEBPACK_IMPORTED_MODULE_0__.staticRenderFns; }\n/* harmony export */ });\n/* harmony import */ var _node_modules_babel_loader_lib_index_js_clonedRuleSet_40_use_0_node_modules_vue_vue_loader_v15_lib_loaders_templateLoader_js_ruleSet_1_rules_3_node_modules_vue_vue_loader_v15_lib_index_js_vue_loader_options_detail_vue_vue_type_template_id_6ae34364__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../../node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!../../../node_modules/@vue/vue-loader-v15/lib/loaders/templateLoader.js??ruleSet[1].rules[3]!../../../node_modules/@vue/vue-loader-v15/lib/index.js??vue-loader-options!./detail.vue?vue&type=template&id=6ae34364 */ \"./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/@vue/vue-loader-v15/lib/loaders/templateLoader.js??ruleSet[1].rules[3]!./node_modules/@vue/vue-loader-v15/lib/index.js??vue-loader-options!./src/views/scene/detail.vue?vue&type=template&id=6ae34364\");\n\n\n//# sourceURL=webpack://my_project/./src/views/scene/detail.vue?\n}");

/***/ })

}]);