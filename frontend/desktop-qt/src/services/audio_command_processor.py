"""
Audio Command Processor
שירות מרכזי לעיבוד פקודות אודיו בשפה טבעית
"""

import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

from .audio_command_interpreter import AudioCommandInterpreter, ParsedCommand, CommandType
from .audio_command_mapper import AudioCommandMapper, ExecutionResult, ExecutionStatus
from .llm_service import LLMService
from .audio_editing_service import AudioEditingService
from .audio_metadata_service import AudioMetadataService


@dataclass
class ProcessingResult:
    """תוצאת עיבוד פקודה מלאה"""
    success: bool
    message: str
    parsed_command: Optional[ParsedCommand] = None
    execution_result: Optional[ExecutionResult] = None
    suggestions: List[str] = None
    warnings: List[str] = None
    errors: List[str] = None
    processing_time: Optional[float] = None
    output_file: Optional[str] = None
    metadata: Dict[str, Any] = None


class AudioCommandProcessor:
    """מעבד פקודות אודיו מרכזי"""
    
    def __init__(self, 
                 llm_service: LLMService,
                 audio_editing_service: AudioEditingService,
                 audio_metadata_service: AudioMetadataService):
        self.llm_service = llm_service
        self.audio_editing_service = audio_editing_service
        self.audio_metadata_service = audio_metadata_service
        
        # יצירת רכיבי המערכת
        self.interpreter = AudioCommandInterpreter(llm_service)
        self.mapper = AudioCommandMapper(audio_editing_service)
        
        self.logger = logging.getLogger(__name__)

    async def process_command(self, 
                            command_text: str, 
                            input_file: str, 
                            context: Optional[Dict] = None) -> ProcessingResult:
        """
        עיבוד פקודה מלאה - מפרשנות ועד ביצוע
        
        Args:
            command_text: טקסט הפקודה בשפה טבעית
            input_file: נתיב לקובץ האודיו
            context: הקשר נוסף (מטאדטה, הגדרות וכו')
            
        Returns:
            ProcessingResult: תוצאת העיבוד המלאה
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Processing command: '{command_text}' for file: {input_file}")
            
            # שלב 1: הכנת הקשר
            enriched_context = await self._prepare_context(input_file, context)
            
            # שלב 2: פרשנות הפקודה
            parsed_command = await self.interpreter.interpret_command(command_text, enriched_context)
            
            if parsed_command.command_type == CommandType.UNKNOWN:
                return ProcessingResult(
                    success=False,
                    message="Could not understand the command",
                    parsed_command=parsed_command,
                    suggestions=parsed_command.suggestions,
                    errors=parsed_command.errors or ["Unknown command"],
                    processing_time=time.time() - start_time
                )
            
            # שלב 3: אימות פרמטרים
            validated_command = self.interpreter.validate_parameters(parsed_command, enriched_context)
            
            if validated_command.errors:
                return ProcessingResult(
                    success=False,
                    message="Command has validation errors",
                    parsed_command=validated_command,
                    errors=validated_command.errors,
                    warnings=validated_command.warnings,
                    processing_time=time.time() - start_time
                )
            
            # שלב 4: ביצוע הפקודה
            execution_result = await self.mapper.execute_command(
                validated_command, 
                input_file, 
                enriched_context
            )
            
            # שלב 5: הכנת התוצאה הסופית
            total_time = time.time() - start_time
            
            return ProcessingResult(
                success=execution_result.status == ExecutionStatus.SUCCESS,
                message=execution_result.message,
                parsed_command=validated_command,
                execution_result=execution_result,
                suggestions=validated_command.suggestions,
                warnings=self._combine_warnings(validated_command.warnings, execution_result.warnings),
                errors=execution_result.errors,
                processing_time=total_time,
                output_file=execution_result.output_file,
                metadata=self._combine_metadata(validated_command, execution_result)
            )
            
        except Exception as e:
            self.logger.error(f"Error processing command: {e}")
            return ProcessingResult(
                success=False,
                message=f"Processing error: {str(e)}",
                errors=[str(e)],
                processing_time=time.time() - start_time
            )

    async def _prepare_context(self, input_file: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """הכנת הקשר מועשר עם מטאדטה של הקובץ"""
        enriched_context = context.copy() if context else {}
        
        try:
            # קבלת מידע על הקובץ
            file_info = await self.audio_editing_service.get_audio_info(input_file)
            if file_info:
                enriched_context['file_info'] = file_info
                enriched_context['duration'] = file_info.get('duration')
                enriched_context['sample_rate'] = file_info.get('sample_rate')
                enriched_context['channels'] = file_info.get('channels')
            
            # קבלת מטאדטה מתקדמת אם זמינה
            try:
                metadata = await self.audio_metadata_service.get_basic_metadata(input_file)
                if metadata:
                    enriched_context['metadata'] = metadata
            except Exception as e:
                self.logger.warning(f"Could not get metadata: {e}")
            
        except Exception as e:
            self.logger.warning(f"Could not prepare context: {e}")
        
        return enriched_context

    def _combine_warnings(self, 
                         interpreter_warnings: Optional[List[str]], 
                         execution_warnings: Optional[List[str]]) -> Optional[List[str]]:
        """שילוב אזהרות מכל השלבים"""
        all_warnings = []
        
        if interpreter_warnings:
            all_warnings.extend(interpreter_warnings)
        
        if execution_warnings:
            all_warnings.extend(execution_warnings)
        
        return all_warnings if all_warnings else None

    def _combine_metadata(self, 
                         parsed_command: ParsedCommand, 
                         execution_result: ExecutionResult) -> Dict[str, Any]:
        """שילוב מטאדטה מכל השלבים"""
        metadata = {
            'command_info': {
                'type': parsed_command.command_type.value,
                'confidence': parsed_command.confidence,
                'original_text': parsed_command.original_text,
                'normalized_text': parsed_command.normalized_text
            },
            'parameters': [
                {
                    'name': param.name,
                    'type': param.type.value,
                    'value': param.value,
                    'unit': param.unit,
                    'valid': param.valid
                }
                for param in parsed_command.parameters
            ]
        }
        
        if execution_result.metadata:
            metadata['execution'] = execution_result.metadata
        
        return metadata

    async def get_command_suggestions(self, 
                                    partial_command: str, 
                                    context: Optional[Dict] = None) -> List[str]:
        """קבלת הצעות לפקודות על בסיס טקסט חלקי"""
        try:
            # ניסיון פרשנות של הטקסט החלקי
            parsed = await self.interpreter.interpret_command(partial_command, context)
            
            if parsed.suggestions:
                return parsed.suggestions
            
            # אם אין הצעות ספציפיות, נחזיר הצעות כלליות
            return self._get_general_suggestions(partial_command)
            
        except Exception as e:
            self.logger.error(f"Error getting suggestions: {e}")
            return self._get_general_suggestions(partial_command)

    def _get_general_suggestions(self, partial_command: str) -> List[str]:
        """הצעות כלליות על בסיס מילות מפתח"""
        partial_lower = partial_command.lower()
        suggestions = []
        
        # הצעות לפי מילות מפתח
        if any(word in partial_lower for word in ['cut', 'trim', 'remove']):
            suggestions.extend([
                "Cut the first 30 seconds",
                "Trim from 1:30 to 2:45",
                "Remove the last 10 seconds"
            ])
        
        if any(word in partial_lower for word in ['volume', 'loud', 'quiet']):
            suggestions.extend([
                "Increase volume by 6dB",
                "Decrease volume by 3dB",
                "Normalize the audio to -3dB"
            ])
        
        if any(word in partial_lower for word in ['fade', 'smooth']):
            suggestions.extend([
                "Add 2-second fade in",
                "Apply fade out",
                "Add fade in and fade out"
            ])
        
        if any(word in partial_lower for word in ['noise', 'clean', 'hum']):
            suggestions.extend([
                "Remove background noise",
                "Clean up the recording",
                "Eliminate 60Hz hum"
            ])
        
        # אם אין התאמות, נחזיר הצעות בסיסיות
        if not suggestions:
            suggestions = [
                "Normalize the audio",
                "Remove background noise",
                "Increase volume by 6dB",
                "Add fade in and fade out",
                "Cut the first 30 seconds"
            ]
        
        return suggestions[:5]  # מגביל ל-5 הצעות

    async def validate_command_before_execution(self, 
                                              command_text: str, 
                                              input_file: str, 
                                              context: Optional[Dict] = None) -> Dict[str, Any]:
        """אימות פקודה לפני ביצוע - לבדיקה מקדימה"""
        try:
            # הכנת הקשר
            enriched_context = await self._prepare_context(input_file, context)
            
            # פרשנות הפקודה
            parsed_command = await self.interpreter.interpret_command(command_text, enriched_context)
            
            # אימות פרמטרים
            validated_command = self.interpreter.validate_parameters(parsed_command, enriched_context)
            
            return {
                'valid': validated_command.command_type != CommandType.UNKNOWN and not validated_command.errors,
                'command_type': validated_command.command_type.value,
                'confidence': validated_command.confidence,
                'parameters': [
                    {
                        'name': param.name,
                        'value': param.value,
                        'unit': param.unit,
                        'valid': param.valid,
                        'error': param.error_message
                    }
                    for param in validated_command.parameters
                ],
                'warnings': validated_command.warnings,
                'errors': validated_command.errors,
                'suggestions': validated_command.suggestions
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'suggestions': self._get_general_suggestions(command_text)
            }

    def get_supported_commands_info(self) -> Dict[str, Any]:
        """מידע על כל הפקודות הנתמכות"""
        supported_commands = {}
        
        for command_type in CommandType:
            if command_type != CommandType.UNKNOWN:
                command_info = self.mapper.get_command_info(command_type)
                help_info = self.interpreter.get_command_help(command_type)
                
                supported_commands[command_type.value] = {
                    **command_info,
                    **help_info
                }
        
        return {
            'supported_commands': supported_commands,
            'total_commands': len(supported_commands),
            'categories': self._get_command_categories()
        }

    def _get_command_categories(self) -> Dict[str, List[str]]:
        """קטגוריזציה של פקודות"""
        return {
            'basic_editing': [
                CommandType.TRIM.value,
                CommandType.VOLUME.value,
                CommandType.FADE.value,
                CommandType.NORMALIZE.value
            ],
            'audio_enhancement': [
                CommandType.NOISE_REDUCTION.value,
                CommandType.EQ.value,
                CommandType.COMPRESS.value
            ],
            'effects': [
                CommandType.REVERB.value,
                CommandType.DELAY.value
            ],
            'conversion': [
                CommandType.CONVERT.value
            ],
            'analysis': [
                CommandType.ANALYZE.value
            ]
        }

    async def get_processing_stats(self) -> Dict[str, Any]:
        """סטטיסטיקות עיבוד"""
        # כאן ניתן להוסיף מעקב אחר סטטיסטיקות
        return {
            'supported_commands': len(self.mapper.get_supported_commands()),
            'interpreter_available': True,
            'mapper_available': True,
            'llm_service_available': self.llm_service is not None,
            'audio_service_available': self.audio_editing_service is not None
        }

    def to_dict(self, processing_result: ProcessingResult) -> Dict[str, Any]:
        """המרת תוצאה למילון לשליחה ב-API"""
        result_dict = {
            'success': processing_result.success,
            'message': processing_result.message,
            'processing_time': processing_result.processing_time,
            'output_file': processing_result.output_file
        }
        
        if processing_result.parsed_command:
            result_dict['parsed_command'] = {
                'command_type': processing_result.parsed_command.command_type.value,
                'confidence': processing_result.parsed_command.confidence,
                'original_text': processing_result.parsed_command.original_text
            }
        
        if processing_result.suggestions:
            result_dict['suggestions'] = processing_result.suggestions
        
        if processing_result.warnings:
            result_dict['warnings'] = processing_result.warnings
        
        if processing_result.errors:
            result_dict['errors'] = processing_result.errors
        
        if processing_result.metadata:
            result_dict['metadata'] = processing_result.metadata
        
        return result_dict