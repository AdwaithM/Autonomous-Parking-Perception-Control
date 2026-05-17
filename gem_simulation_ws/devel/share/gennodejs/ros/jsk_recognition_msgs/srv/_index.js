
"use strict";

let UpdateOffset = require('./UpdateOffset.js')
let SetDepthCalibrationParameter = require('./SetDepthCalibrationParameter.js')
let RobotPickupReleasePoint = require('./RobotPickupReleasePoint.js')
let WhiteBalance = require('./WhiteBalance.js')
let SetTemplate = require('./SetTemplate.js')
let EnvironmentLock = require('./EnvironmentLock.js')
let SwitchTopic = require('./SwitchTopic.js')
let ICPAlignWithBox = require('./ICPAlignWithBox.js')
let CallSnapIt = require('./CallSnapIt.js')
let WhiteBalancePoints = require('./WhiteBalancePoints.js')
let TransformScreenpoint = require('./TransformScreenpoint.js')
let SaveMesh = require('./SaveMesh.js')
let CheckCircle = require('./CheckCircle.js')
let ICPAlign = require('./ICPAlign.js')
let SnapFootstep = require('./SnapFootstep.js')
let CheckCollision = require('./CheckCollision.js')
let TowerRobotMoveCommand = require('./TowerRobotMoveCommand.js')
let SetLabels = require('./SetLabels.js')
let SetPointCloud2 = require('./SetPointCloud2.js')
let TowerPickUp = require('./TowerPickUp.js')
let CallPolygon = require('./CallPolygon.js')
let EuclideanSegment = require('./EuclideanSegment.js')
let PolygonOnEnvironment = require('./PolygonOnEnvironment.js')
let NonMaximumSuppression = require('./NonMaximumSuppression.js')

module.exports = {
  UpdateOffset: UpdateOffset,
  SetDepthCalibrationParameter: SetDepthCalibrationParameter,
  RobotPickupReleasePoint: RobotPickupReleasePoint,
  WhiteBalance: WhiteBalance,
  SetTemplate: SetTemplate,
  EnvironmentLock: EnvironmentLock,
  SwitchTopic: SwitchTopic,
  ICPAlignWithBox: ICPAlignWithBox,
  CallSnapIt: CallSnapIt,
  WhiteBalancePoints: WhiteBalancePoints,
  TransformScreenpoint: TransformScreenpoint,
  SaveMesh: SaveMesh,
  CheckCircle: CheckCircle,
  ICPAlign: ICPAlign,
  SnapFootstep: SnapFootstep,
  CheckCollision: CheckCollision,
  TowerRobotMoveCommand: TowerRobotMoveCommand,
  SetLabels: SetLabels,
  SetPointCloud2: SetPointCloud2,
  TowerPickUp: TowerPickUp,
  CallPolygon: CallPolygon,
  EuclideanSegment: EuclideanSegment,
  PolygonOnEnvironment: PolygonOnEnvironment,
  NonMaximumSuppression: NonMaximumSuppression,
};
