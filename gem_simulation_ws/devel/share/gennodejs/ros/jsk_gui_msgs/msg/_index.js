
"use strict";

let VoiceMessage = require('./VoiceMessage.js');
let Touch = require('./Touch.js');
let TouchEvent = require('./TouchEvent.js');
let SlackMessage = require('./SlackMessage.js');
let DeviceSensor = require('./DeviceSensor.js');
let Action = require('./Action.js');
let Tablet = require('./Tablet.js');
let MultiTouch = require('./MultiTouch.js');
let Gravity = require('./Gravity.js');
let MagneticField = require('./MagneticField.js');
let AndroidSensor = require('./AndroidSensor.js');

module.exports = {
  VoiceMessage: VoiceMessage,
  Touch: Touch,
  TouchEvent: TouchEvent,
  SlackMessage: SlackMessage,
  DeviceSensor: DeviceSensor,
  Action: Action,
  Tablet: Tablet,
  MultiTouch: MultiTouch,
  Gravity: Gravity,
  MagneticField: MagneticField,
  AndroidSensor: AndroidSensor,
};
