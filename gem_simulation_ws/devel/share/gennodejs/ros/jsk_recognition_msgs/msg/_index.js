
"use strict";

let ContactSensor = require('./ContactSensor.js');
let HumanSkeletonArray = require('./HumanSkeletonArray.js');
let SparseOccupancyGridColumn = require('./SparseOccupancyGridColumn.js');
let ObjectArray = require('./ObjectArray.js');
let Circle2DArray = require('./Circle2DArray.js');
let SimpleHandle = require('./SimpleHandle.js');
let Accuracy = require('./Accuracy.js');
let ModelCoefficientsArray = require('./ModelCoefficientsArray.js');
let ClusterPointIndices = require('./ClusterPointIndices.js');
let BoundingBox = require('./BoundingBox.js');
let HistogramWithRangeArray = require('./HistogramWithRangeArray.js');
let Circle2D = require('./Circle2D.js');
let ColorHistogram = require('./ColorHistogram.js');
let ContactSensorArray = require('./ContactSensorArray.js');
let PosedCameraInfo = require('./PosedCameraInfo.js');
let PlotDataArray = require('./PlotDataArray.js');
let ClassificationResult = require('./ClassificationResult.js');
let PlotData = require('./PlotData.js');
let SimpleOccupancyGrid = require('./SimpleOccupancyGrid.js');
let ParallelEdgeArray = require('./ParallelEdgeArray.js');
let ICPResult = require('./ICPResult.js');
let TorusArray = require('./TorusArray.js');
let PointsArray = require('./PointsArray.js');
let SparseImage = require('./SparseImage.js');
let SparseOccupancyGrid = require('./SparseOccupancyGrid.js');
let BoundingBoxMovement = require('./BoundingBoxMovement.js');
let Object = require('./Object.js');
let SimpleOccupancyGridArray = require('./SimpleOccupancyGridArray.js');
let TrackerStatus = require('./TrackerStatus.js');
let SparseOccupancyGridCell = require('./SparseOccupancyGridCell.js');
let Segment = require('./Segment.js');
let TimeRange = require('./TimeRange.js');
let Torus = require('./Torus.js');
let SegmentArray = require('./SegmentArray.js');
let HumanSkeleton = require('./HumanSkeleton.js');
let SnapItRequest = require('./SnapItRequest.js');
let BoundingBoxArrayWithCameraInfo = require('./BoundingBoxArrayWithCameraInfo.js');
let Spectrum = require('./Spectrum.js');
let VectorArray = require('./VectorArray.js');
let Rect = require('./Rect.js');
let HistogramWithRange = require('./HistogramWithRange.js');
let HistogramWithRangeBin = require('./HistogramWithRangeBin.js');
let HeightmapConfig = require('./HeightmapConfig.js');
let RotatedRect = require('./RotatedRect.js');
let DepthCalibrationParameter = require('./DepthCalibrationParameter.js');
let BoolStamped = require('./BoolStamped.js');
let ImageDifferenceValue = require('./ImageDifferenceValue.js');
let Line = require('./Line.js');
let SparseOccupancyGridArray = require('./SparseOccupancyGridArray.js');
let ParallelEdge = require('./ParallelEdge.js');
let SegmentStamped = require('./SegmentStamped.js');
let PolygonArray = require('./PolygonArray.js');
let ColorHistogramArray = require('./ColorHistogramArray.js');
let Histogram = require('./Histogram.js');
let LineArray = require('./LineArray.js');
let LabelArray = require('./LabelArray.js');
let BoundingBoxArray = require('./BoundingBoxArray.js');
let WeightedPoseArray = require('./WeightedPoseArray.js');
let RotatedRectStamped = require('./RotatedRectStamped.js');
let SlicedPointCloud = require('./SlicedPointCloud.js');
let DepthErrorResult = require('./DepthErrorResult.js');
let PeoplePoseArray = require('./PeoplePoseArray.js');
let PeoplePose = require('./PeoplePose.js');
let TrackingStatus = require('./TrackingStatus.js');
let Int32Stamped = require('./Int32Stamped.js');
let RectArray = require('./RectArray.js');
let Label = require('./Label.js');

module.exports = {
  ContactSensor: ContactSensor,
  HumanSkeletonArray: HumanSkeletonArray,
  SparseOccupancyGridColumn: SparseOccupancyGridColumn,
  ObjectArray: ObjectArray,
  Circle2DArray: Circle2DArray,
  SimpleHandle: SimpleHandle,
  Accuracy: Accuracy,
  ModelCoefficientsArray: ModelCoefficientsArray,
  ClusterPointIndices: ClusterPointIndices,
  BoundingBox: BoundingBox,
  HistogramWithRangeArray: HistogramWithRangeArray,
  Circle2D: Circle2D,
  ColorHistogram: ColorHistogram,
  ContactSensorArray: ContactSensorArray,
  PosedCameraInfo: PosedCameraInfo,
  PlotDataArray: PlotDataArray,
  ClassificationResult: ClassificationResult,
  PlotData: PlotData,
  SimpleOccupancyGrid: SimpleOccupancyGrid,
  ParallelEdgeArray: ParallelEdgeArray,
  ICPResult: ICPResult,
  TorusArray: TorusArray,
  PointsArray: PointsArray,
  SparseImage: SparseImage,
  SparseOccupancyGrid: SparseOccupancyGrid,
  BoundingBoxMovement: BoundingBoxMovement,
  Object: Object,
  SimpleOccupancyGridArray: SimpleOccupancyGridArray,
  TrackerStatus: TrackerStatus,
  SparseOccupancyGridCell: SparseOccupancyGridCell,
  Segment: Segment,
  TimeRange: TimeRange,
  Torus: Torus,
  SegmentArray: SegmentArray,
  HumanSkeleton: HumanSkeleton,
  SnapItRequest: SnapItRequest,
  BoundingBoxArrayWithCameraInfo: BoundingBoxArrayWithCameraInfo,
  Spectrum: Spectrum,
  VectorArray: VectorArray,
  Rect: Rect,
  HistogramWithRange: HistogramWithRange,
  HistogramWithRangeBin: HistogramWithRangeBin,
  HeightmapConfig: HeightmapConfig,
  RotatedRect: RotatedRect,
  DepthCalibrationParameter: DepthCalibrationParameter,
  BoolStamped: BoolStamped,
  ImageDifferenceValue: ImageDifferenceValue,
  Line: Line,
  SparseOccupancyGridArray: SparseOccupancyGridArray,
  ParallelEdge: ParallelEdge,
  SegmentStamped: SegmentStamped,
  PolygonArray: PolygonArray,
  ColorHistogramArray: ColorHistogramArray,
  Histogram: Histogram,
  LineArray: LineArray,
  LabelArray: LabelArray,
  BoundingBoxArray: BoundingBoxArray,
  WeightedPoseArray: WeightedPoseArray,
  RotatedRectStamped: RotatedRectStamped,
  SlicedPointCloud: SlicedPointCloud,
  DepthErrorResult: DepthErrorResult,
  PeoplePoseArray: PeoplePoseArray,
  PeoplePose: PeoplePose,
  TrackingStatus: TrackingStatus,
  Int32Stamped: Int32Stamped,
  RectArray: RectArray,
  Label: Label,
};
