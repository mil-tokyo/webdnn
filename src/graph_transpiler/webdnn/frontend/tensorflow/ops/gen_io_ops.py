import tensorflow as tf

from webdnn.frontend.tensorflow.converter import TensorFlowConverter


@TensorFlowConverter.register_handler("FixedLengthRecordReader")
def fixed_length_record_reader_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("FixedLengthRecordReaderV2")
def fixed_length_record_reader_v2_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("IdentityReader")
def identity_reader_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("IdentityReaderV2")
def identity_reader_v2_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("LMDBReader")
def lmdb_reader_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("MatchingFiles")
def matching_files_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("MergeV2Checkpoints")
def merge_v2_checkpoints_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("ReadFile")
def read_file_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("ReaderNumRecordsProduced")
def reader_num_records_produced_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("ReaderNumRecordsProducedV2")
def reader_num_records_produced_v2_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("ReaderNumWorkUnitsCompleted")
def reader_num_work_units_completed_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("ReaderNumWorkUnitsCompletedV2")
def reader_num_work_units_completed_v2_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("ReaderRead")
def reader_read_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("ReaderReadUpTo")
def reader_read_up_to_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("ReaderReadUpToV2")
def reader_read_up_to_v2_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("ReaderReadV2")
def reader_read_v2_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("ReaderReset")
def reader_reset_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("ReaderResetV2")
def reader_reset_v2_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("ReaderRestoreState")
def reader_restore_state_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("ReaderRestoreStateV2")
def reader_restore_state_v2_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("ReaderSerializeState")
def reader_serialize_state_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("ReaderSerializeStateV2")
def reader_serialize_state_v2_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Restore")
def restore_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("RestoreSlice")
def restore_slice_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("RestoreV2")
def restore_v2_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Save")
def save_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("SaveSlices")
def save_slices_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("SaveV2")
def save_v2_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("ShardedFilename")
def sharded_filename_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("ShardedFilespec")
def sharded_filespec_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("TFRecordReader")
def tf_record_reader_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("TFRecordReaderV2")
def tf_record_reader_v2_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("TextLineReader")
def text_line_reader_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("TextLineReaderV2")
def text_line_reader_v2_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("WholeFileReader")
def whole_file_reader_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("WholeFileReaderV2")
def whole_file_reader_v2_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("WriteFile")
def write_file_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")
