"""
Audio Command Mapper
מיפוי פקודות מפורשות לפונקציות עריכת אודיו
"""

import logging
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass
from enum import Enum

from .command_interpreter import ParsedCommand, CommandType, CommandParameter
from backend.services.audio.editing import AudioEditingService


class ExecutionStatus(Enum):
    """סטטוס ביצוע פקודה"""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    SKIPPED = "skipped"


@dataclass
class ExecutionResult:
    """תוצאת ביצוע פקודה"""
    status: ExecutionStatus
    message: str
    output_file: Optional[str] = None
    processing_time: Optional[float] = None
    warnings: List[str] = None
    errors: List[str] = None
    metadata: Dict[str, Any] = None


class AudioCommandMapper:
    """מיפוי פקודות לפונקציות עריכה"""
    
    def __init__(self, audio_editing_service: AudioEditingService):
        self.audio_editing_service = audio_editing_service
        self.logger = logging.getLogger(__name__)
        
        # מיפוי פקודות לפונקציות
        self.command_mappings = {
            CommandType.TRIM: self._execute_trim,
            CommandType.VOLUME: self._execute_volume,
            CommandType.FADE: self._execute_fade,
            CommandType.NORMALIZE: self._execute_normalize,
            CommandType.NOISE_REDUCTION: self._execute_noise_reduction,
            CommandType.EQ: self._execute_eq,
            CommandType.REVERB: self._execute_reverb,
            CommandType.DELAY: self._execute_delay,
            CommandType.COMPRESS: self._execute_compress,
            CommandType.CONVERT: self._execute_convert,
            CommandType.ANALYZE: self._execute_analyze,
        }

    async def execute_command(self, parsed_command: ParsedCommand, input_file: str, context: Optional[Dict] = None) -> ExecutionResult:
        """
        ביצוע פקודה מפורשת
        
        Args:
            parsed_command: פקודה מפורשת
            input_file: קובץ קלט
            context: הקשר נוסף
            
        Returns:
            ExecutionResult: תוצאת הביצוע
        """
        try:
            self.logger.info(f"Executing command: {parsed_command.command_type.value}")
            
            # בדיקה שהפקודה נתמכת
            if parsed_command.command_type not in self.command_mappings:
                return ExecutionResult(
                    status=ExecutionStatus.FAILED,
                    message=f"Command type {parsed_command.command_type.value} is not supported",
                    errors=[f"Unsupported command: {parsed_command.command_type.value}"]
                )
            
            # בדיקה שאין שגיאות בפרשנות
            if parsed_command.errors:
                return ExecutionResult(
                    status=ExecutionStatus.FAILED,
                    message="Command has parsing errors",
                    errors=parsed_command.errors
                )
            
            # בדיקה שכל הפרמטרים תקינים
            invalid_params = [p for p in parsed_command.parameters if not p.valid]
            if invalid_params:
                error_messages = [p.error_message for p in invalid_params if p.error_message]
                return ExecutionResult(
                    status=ExecutionStatus.FAILED,
                    message="Command has invalid parameters",
                    errors=error_messages
                )
            
            # ביצוע הפקודה
            execution_func = self.command_mappings[parsed_command.command_type]
            result = await execution_func(parsed_command, input_file, context)
            
            # הוספת אזהרות מהפרשנות
            if parsed_command.warnings:
                if result.warnings:
                    result.warnings.extend(parsed_command.warnings)
                else:
                    result.warnings = parsed_command.warnings.copy()
            
            self.logger.info(f"Command executed: {result.status.value}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing command: {e}")
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                message=f"Execution error: {str(e)}",
                errors=[str(e)]
            )

    async def _execute_trim(self, parsed_command: ParsedCommand, input_file: str, context: Optional[Dict] = None) -> ExecutionResult:
        """ביצוע פקודת חיתוך"""
        try:
            # חילוץ פרמטרים
            params = self._extract_parameters(parsed_command.parameters)
            
            start_time = params.get('start_time', 0.0)
            end_time = params.get('end_time')
            duration = params.get('duration')
            end_offset = params.get('end_offset')
            
            # קביעת זמני התחלה וסיום
            if end_time is not None:
                # חיתוך בין זמנים ספציפיים
                trim_start = start_time
                trim_end = end_time
            elif duration is not None:
                # חיתוך לפי משך זמן
                trim_start = start_time
                trim_end = start_time + duration
            elif end_offset is not None:
                # חיתוך מהסוף
                # נצטרך לקבל את משך הקובץ
                file_info = await self.audio_editing_service.get_audio_info(input_file)
                if not file_info:
                    return ExecutionResult(
                        status=ExecutionStatus.FAILED,
                        message="Could not get audio file information",
                        errors=["Failed to read audio file info"]
                    )
                
                total_duration = file_info.get('duration', 0)
                trim_start = 0
                trim_end = total_duration - end_offset
            else:
                return ExecutionResult(
                    status=ExecutionStatus.FAILED,
                    message="Missing required parameters for trim operation",
                    errors=["No valid time parameters provided"]
                )
            
            # ביצוע החיתוך
            result = await self.audio_editing_service.trim_audio(
                input_file=input_file,
                start_time=trim_start,
                end_time=trim_end
            )
            
            if result.get('success'):
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS,
                    message=f"Audio trimmed from {trim_start}s to {trim_end}s",
                    output_file=result.get('output_file'),
                    processing_time=result.get('processing_time'),
                    metadata={
                        'start_time': trim_start,
                        'end_time': trim_end,
                        'duration': trim_end - trim_start
                    }
                )
            else:
                return ExecutionResult(
                    status=ExecutionStatus.FAILED,
                    message="Trim operation failed",
                    errors=[result.get('error', 'Unknown error')]
                )
                
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                message=f"Trim execution error: {str(e)}",
                errors=[str(e)]
            )

    async def _execute_volume(self, parsed_command: ParsedCommand, input_file: str, context: Optional[Dict] = None) -> ExecutionResult:
        """ביצוע פקודת עוצמת קול"""
        try:
            params = self._extract_parameters(parsed_command.parameters)
            volume_change = params.get('volume_change', 0.0)
            
            # ביצוע שינוי עוצמת הקול
            result = await self.audio_editing_service.adjust_volume(
                input_file=input_file,
                volume_change_db=volume_change
            )
            
            if result.get('success'):
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS,
                    message=f"Volume adjusted by {volume_change:+.1f}dB",
                    output_file=result.get('output_file'),
                    processing_time=result.get('processing_time'),
                    metadata={'volume_change_db': volume_change}
                )
            else:
                return ExecutionResult(
                    status=ExecutionStatus.FAILED,
                    message="Volume adjustment failed",
                    errors=[result.get('error', 'Unknown error')]
                )
                
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                message=f"Volume execution error: {str(e)}",
                errors=[str(e)]
            )

    async def _execute_fade(self, parsed_command: ParsedCommand, input_file: str, context: Optional[Dict] = None) -> ExecutionResult:
        """ביצוע פקודת fade"""
        try:
            params = self._extract_parameters(parsed_command.parameters)
            duration = params.get('duration', 2.0)
            fade_type = params.get('type', 'both')
            
            # ביצוע ה-fade
            result = await self.audio_editing_service.apply_fade(
                input_file=input_file,
                fade_in_duration=duration if fade_type in ['in', 'both'] else 0,
                fade_out_duration=duration if fade_type in ['out', 'both'] else 0
            )
            
            if result.get('success'):
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS,
                    message=f"Applied {duration}s fade {fade_type}",
                    output_file=result.get('output_file'),
                    processing_time=result.get('processing_time'),
                    metadata={
                        'fade_duration': duration,
                        'fade_type': fade_type
                    }
                )
            else:
                return ExecutionResult(
                    status=ExecutionStatus.FAILED,
                    message="Fade operation failed",
                    errors=[result.get('error', 'Unknown error')]
                )
                
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                message=f"Fade execution error: {str(e)}",
                errors=[str(e)]
            )

    async def _execute_normalize(self, parsed_command: ParsedCommand, input_file: str, context: Optional[Dict] = None) -> ExecutionResult:
        """ביצוע פקודת נורמליזציה"""
        try:
            params = self._extract_parameters(parsed_command.parameters)
            target_level = params.get('target_level', -3.0)
            norm_type = params.get('type', 'peak')
            
            # ביצוע הנורמליזציה
            result = await self.audio_editing_service.normalize_audio(
                input_file=input_file,
                target_level_db=target_level,
                normalization_type=norm_type
            )
            
            if result.get('success'):
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS,
                    message=f"Audio normalized to {target_level}dB ({norm_type})",
                    output_file=result.get('output_file'),
                    processing_time=result.get('processing_time'),
                    metadata={
                        'target_level_db': target_level,
                        'normalization_type': norm_type
                    }
                )
            else:
                return ExecutionResult(
                    status=ExecutionStatus.FAILED,
                    message="Normalization failed",
                    errors=[result.get('error', 'Unknown error')]
                )
                
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                message=f"Normalize execution error: {str(e)}",
                errors=[str(e)]
            )

    async def _execute_noise_reduction(self, parsed_command: ParsedCommand, input_file: str, context: Optional[Dict] = None) -> ExecutionResult:
        """ביצוע פקודת הפחתת רעש"""
        try:
            params = self._extract_parameters(parsed_command.parameters)
            amount = params.get('amount', 50.0)
            noise_type = params.get('noise_type', 'auto')
            
            # ביצוע הפחתת הרעש
            result = await self.audio_editing_service.reduce_noise(
                input_file=input_file,
                reduction_amount=amount / 100.0,  # המרה לאחוזים
                noise_type=noise_type
            )
            
            if result.get('success'):
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS,
                    message=f"Noise reduced by {amount}% ({noise_type})",
                    output_file=result.get('output_file'),
                    processing_time=result.get('processing_time'),
                    metadata={
                        'reduction_amount': amount,
                        'noise_type': noise_type
                    }
                )
            else:
                return ExecutionResult(
                    status=ExecutionStatus.FAILED,
                    message="Noise reduction failed",
                    errors=[result.get('error', 'Unknown error')]
                )
                
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                message=f"Noise reduction execution error: {str(e)}",
                errors=[str(e)]
            )

    async def _execute_eq(self, parsed_command: ParsedCommand, input_file: str, context: Optional[Dict] = None) -> ExecutionResult:
        """ביצוע פקודת EQ"""
        try:
            params = self._extract_parameters(parsed_command.parameters)
            frequency = params.get('frequency', 1000)
            gain = params.get('gain', 0.0)
            q_factor = params.get('q_factor', 1.0)
            filter_type = params.get('filter_type', 'bell')
            
            # ביצוע ה-EQ
            result = await self.audio_editing_service.apply_eq(
                input_file=input_file,
                frequency=frequency,
                gain_db=gain,
                q_factor=q_factor,
                filter_type=filter_type
            )
            
            if result.get('success'):
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS,
                    message=f"EQ applied: {gain:+.1f}dB at {frequency}Hz",
                    output_file=result.get('output_file'),
                    processing_time=result.get('processing_time'),
                    metadata={
                        'frequency': frequency,
                        'gain_db': gain,
                        'q_factor': q_factor,
                        'filter_type': filter_type
                    }
                )
            else:
                return ExecutionResult(
                    status=ExecutionStatus.FAILED,
                    message="EQ operation failed",
                    errors=[result.get('error', 'Unknown error')]
                )
                
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                message=f"EQ execution error: {str(e)}",
                errors=[str(e)]
            )

    async def _execute_reverb(self, parsed_command: ParsedCommand, input_file: str, context: Optional[Dict] = None) -> ExecutionResult:
        """ביצוע פקודת reverb"""
        try:
            params = self._extract_parameters(parsed_command.parameters)
            reverb_type = params.get('type', 'hall')
            decay_time = params.get('decay_time', 2.0)
            wet_dry_mix = params.get('wet_dry_mix', 30.0)
            
            # ביצוע ה-reverb
            result = await self.audio_editing_service.apply_reverb(
                input_file=input_file,
                reverb_type=reverb_type,
                decay_time=decay_time,
                wet_dry_mix=wet_dry_mix / 100.0
            )
            
            if result.get('success'):
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS,
                    message=f"{reverb_type.title()} reverb applied ({decay_time}s decay)",
                    output_file=result.get('output_file'),
                    processing_time=result.get('processing_time'),
                    metadata={
                        'reverb_type': reverb_type,
                        'decay_time': decay_time,
                        'wet_dry_mix': wet_dry_mix
                    }
                )
            else:
                return ExecutionResult(
                    status=ExecutionStatus.FAILED,
                    message="Reverb operation failed",
                    errors=[result.get('error', 'Unknown error')]
                )
                
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                message=f"Reverb execution error: {str(e)}",
                errors=[str(e)]
            )

    async def _execute_delay(self, parsed_command: ParsedCommand, input_file: str, context: Optional[Dict] = None) -> ExecutionResult:
        """ביצוע פקודת delay"""
        try:
            params = self._extract_parameters(parsed_command.parameters)
            delay_time = params.get('delay_time', 0.25)
            feedback = params.get('feedback', 0.3)
            wet_dry_mix = params.get('wet_dry_mix', 25.0)
            
            # ביצוע ה-delay
            result = await self.audio_editing_service.apply_delay(
                input_file=input_file,
                delay_time=delay_time,
                feedback=feedback,
                wet_dry_mix=wet_dry_mix / 100.0
            )
            
            if result.get('success'):
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS,
                    message=f"Delay applied ({delay_time*1000:.0f}ms)",
                    output_file=result.get('output_file'),
                    processing_time=result.get('processing_time'),
                    metadata={
                        'delay_time': delay_time,
                        'feedback': feedback,
                        'wet_dry_mix': wet_dry_mix
                    }
                )
            else:
                return ExecutionResult(
                    status=ExecutionStatus.FAILED,
                    message="Delay operation failed",
                    errors=[result.get('error', 'Unknown error')]
                )
                
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                message=f"Delay execution error: {str(e)}",
                errors=[str(e)]
            )

    async def _execute_compress(self, parsed_command: ParsedCommand, input_file: str, context: Optional[Dict] = None) -> ExecutionResult:
        """ביצוע פקודת compression"""
        try:
            params = self._extract_parameters(parsed_command.parameters)
            ratio = params.get('ratio', 3.0)
            threshold = params.get('threshold', -20.0)
            attack = params.get('attack', 0.003)
            release = params.get('release', 0.1)
            
            # ביצוע ה-compression
            result = await self.audio_editing_service.apply_compression(
                input_file=input_file,
                ratio=ratio,
                threshold_db=threshold,
                attack_time=attack,
                release_time=release
            )
            
            if result.get('success'):
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS,
                    message=f"Compression applied ({ratio}:1 ratio)",
                    output_file=result.get('output_file'),
                    processing_time=result.get('processing_time'),
                    metadata={
                        'ratio': ratio,
                        'threshold_db': threshold,
                        'attack_time': attack,
                        'release_time': release
                    }
                )
            else:
                return ExecutionResult(
                    status=ExecutionStatus.FAILED,
                    message="Compression operation failed",
                    errors=[result.get('error', 'Unknown error')]
                )
                
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                message=f"Compression execution error: {str(e)}",
                errors=[str(e)]
            )

    async def _execute_convert(self, parsed_command: ParsedCommand, input_file: str, context: Optional[Dict] = None) -> ExecutionResult:
        """ביצוע פקודת המרה"""
        try:
            params = self._extract_parameters(parsed_command.parameters)
            output_format = params.get('format', 'wav')
            sample_rate = params.get('sample_rate')
            bit_depth = params.get('bit_depth')
            channels = params.get('channels')
            
            # ביצוע ההמרה
            result = await self.audio_editing_service.convert_format(
                input_file=input_file,
                output_format=output_format,
                sample_rate=sample_rate,
                bit_depth=bit_depth,
                channels=channels
            )
            
            if result.get('success'):
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS,
                    message=f"Audio converted to {output_format.upper()}",
                    output_file=result.get('output_file'),
                    processing_time=result.get('processing_time'),
                    metadata={
                        'output_format': output_format,
                        'sample_rate': sample_rate,
                        'bit_depth': bit_depth,
                        'channels': channels
                    }
                )
            else:
                return ExecutionResult(
                    status=ExecutionStatus.FAILED,
                    message="Format conversion failed",
                    errors=[result.get('error', 'Unknown error')]
                )
                
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                message=f"Convert execution error: {str(e)}",
                errors=[str(e)]
            )

    async def _execute_analyze(self, parsed_command: ParsedCommand, input_file: str, context: Optional[Dict] = None) -> ExecutionResult:
        """ביצוע פקודת ניתוח"""
        try:
            params = self._extract_parameters(parsed_command.parameters)
            analysis_type = params.get('analysis_type', 'full')
            
            # ביצוע הניתוח
            result = await self.audio_editing_service.analyze_audio(
                input_file=input_file,
                analysis_type=analysis_type
            )
            
            if result.get('success'):
                analysis_data = result.get('analysis', {})
                
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS,
                    message=f"Audio analysis completed ({analysis_type})",
                    processing_time=result.get('processing_time'),
                    metadata=analysis_data
                )
            else:
                return ExecutionResult(
                    status=ExecutionStatus.FAILED,
                    message="Audio analysis failed",
                    errors=[result.get('error', 'Unknown error')]
                )
                
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                message=f"Analysis execution error: {str(e)}",
                errors=[str(e)]
            )

    def _extract_parameters(self, parameters: List[CommandParameter]) -> Dict[str, Any]:
        """חילוץ פרמטרים למילון"""
        return {param.name: param.value for param in parameters if param.valid}

    def get_supported_commands(self) -> List[str]:
        """קבלת רשימת פקודות נתמכות"""
        return [cmd.value for cmd in self.command_mappings.keys()]

    def get_command_info(self, command_type: CommandType) -> Dict[str, Any]:
        """קבלת מידע על פקודה ספציפית"""
        if command_type not in self.command_mappings:
            return {"error": "Command not supported"}
        
        # מידע בסיסי על הפקודה
        command_info = {
            "command_type": command_type.value,
            "supported": True,
            "description": self._get_command_description(command_type),
            "required_parameters": self._get_required_parameters(command_type),
            "optional_parameters": self._get_optional_parameters(command_type)
        }
        
        return command_info

    def _get_command_description(self, command_type: CommandType) -> str:
        """תיאור הפקודה"""
        descriptions = {
            CommandType.TRIM: "Cut or remove parts of the audio",
            CommandType.VOLUME: "Adjust audio volume levels",
            CommandType.FADE: "Add fade in/out effects",
            CommandType.NORMALIZE: "Normalize audio levels",
            CommandType.NOISE_REDUCTION: "Remove unwanted noise",
            CommandType.EQ: "Apply equalization",
            CommandType.REVERB: "Add reverb effects",
            CommandType.DELAY: "Add delay/echo effects",
            CommandType.COMPRESS: "Apply dynamic range compression",
            CommandType.CONVERT: "Convert audio format",
            CommandType.ANALYZE: "Analyze audio properties"
        }
        return descriptions.get(command_type, "Unknown command")

    def _get_required_parameters(self, command_type: CommandType) -> List[str]:
        """פרמטרים נדרשים"""
        required = {
            CommandType.TRIM: ["start_time", "end_time"],
            CommandType.VOLUME: ["volume_change"],
            CommandType.FADE: ["duration"],
            CommandType.NORMALIZE: [],
            CommandType.NOISE_REDUCTION: [],
            CommandType.EQ: ["frequency", "gain"],
            CommandType.REVERB: [],
            CommandType.DELAY: [],
            CommandType.COMPRESS: [],
            CommandType.CONVERT: ["format"],
            CommandType.ANALYZE: []
        }
        return required.get(command_type, [])

    def _get_optional_parameters(self, command_type: CommandType) -> List[str]:
        """פרמטרים אופציונליים"""
        optional = {
            CommandType.TRIM: ["duration"],
            CommandType.VOLUME: [],
            CommandType.FADE: ["type"],
            CommandType.NORMALIZE: ["target_level", "type"],
            CommandType.NOISE_REDUCTION: ["amount", "noise_type"],
            CommandType.EQ: ["q_factor", "filter_type"],
            CommandType.REVERB: ["type", "decay_time", "wet_dry_mix"],
            CommandType.DELAY: ["delay_time", "feedback", "wet_dry_mix"],
            CommandType.COMPRESS: ["ratio", "threshold", "attack", "release"],
            CommandType.CONVERT: ["sample_rate", "bit_depth", "channels"],
            CommandType.ANALYZE: ["analysis_type"]
        }
        return optional.get(command_type, [])
