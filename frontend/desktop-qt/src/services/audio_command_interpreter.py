"""
Audio Command Interpreter Service
מנוע פרשנות פקודות אודיו בשפה טבעית
"""

import re
import json
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime

from .llm_service import LLMService


class CommandType(Enum):
    """סוגי פקודות אודיו"""
    TRIM = "trim"
    VOLUME = "volume"
    FADE = "fade"
    NORMALIZE = "normalize"
    NOISE_REDUCTION = "noise_reduction"
    EQ = "eq"
    REVERB = "reverb"
    DELAY = "delay"
    COMPRESS = "compress"
    CONVERT = "convert"
    ANALYZE = "analyze"
    UNKNOWN = "unknown"


class ParameterType(Enum):
    """סוגי פרמטרים"""
    TIME = "time"
    VOLUME_DB = "volume_db"
    PERCENTAGE = "percentage"
    FREQUENCY = "frequency"
    BOOLEAN = "boolean"
    STRING = "string"
    NUMBER = "number"


@dataclass
class CommandParameter:
    """פרמטר פקודה"""
    name: str
    type: ParameterType
    value: Any
    unit: Optional[str] = None
    valid: bool = True
    error_message: Optional[str] = None


@dataclass
class ParsedCommand:
    """פקודה מפורשת"""
    command_type: CommandType
    confidence: float
    parameters: List[CommandParameter]
    original_text: str
    normalized_text: str
    suggestions: List[str] = None
    warnings: List[str] = None
    errors: List[str] = None


class AudioCommandInterpreter:
    """מנוע פרשנות פקודות אודיו"""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.logger = logging.getLogger(__name__)
        
        # דפוסי פקודות בסיסיים
        self.command_patterns = {
            CommandType.TRIM: [
                r"(?:cut|trim|remove)\s+(?:the\s+)?(?:first|last|beginning|end)\s+(\d+(?:\.\d+)?)\s*(seconds?|minutes?|s|m)",
                r"(?:cut|trim)\s+from\s+(\d+(?::\d+)?(?:\.\d+)?)\s+to\s+(\d+(?::\d+)?(?:\.\d+)?)",
                r"(?:extract|keep)\s+(?:from\s+)?(\d+(?::\d+)?(?:\.\d+)?)\s+(?:to\s+)?(\d+(?::\d+)?(?:\.\d+)?)",
            ],
            CommandType.VOLUME: [
                r"(?:increase|boost|raise)\s+(?:the\s+)?volume\s+(?:by\s+)?(\d+(?:\.\d+)?)\s*(?:db|decibels?|%|percent)?",
                r"(?:decrease|lower|reduce)\s+(?:the\s+)?volume\s+(?:by\s+)?(\d+(?:\.\d+)?)\s*(?:db|decibels?|%|percent)?",
                r"(?:set|adjust)\s+(?:the\s+)?volume\s+(?:to\s+)?([+-]?\d+(?:\.\d+)?)\s*(?:db|decibels?|%|percent)?",
            ],
            CommandType.FADE: [
                r"(?:add|apply)\s+(?:a\s+)?(\d+(?:\.\d+)?)\s*(?:second|s)?\s+fade\s+(?:in|out)",
                r"(?:fade\s+(?:in|out))\s+(?:for\s+)?(\d+(?:\.\d+)?)\s*(?:seconds?|s)?",
                r"(?:add|apply)\s+fade\s+(?:in\s+and\s+out|effects?)",
            ],
            CommandType.NORMALIZE: [
                r"normalize\s+(?:the\s+)?audio\s+(?:to\s+)?([+-]?\d+(?:\.\d+)?)\s*(?:db|decibels?)?",
                r"normalize\s+(?:to\s+)?([+-]?\d+(?:\.\d+)?)\s*(?:db|decibels?)?\s+(?:peak|rms)",
                r"(?:apply\s+)?(?:peak|rms)\s+normalization",
            ],
            CommandType.NOISE_REDUCTION: [
                r"(?:remove|reduce|eliminate)\s+(?:background\s+)?noise",
                r"(?:clean\s+up|denoise)\s+(?:the\s+)?(?:recording|audio)",
                r"(?:remove|eliminate)\s+(?:hum|hiss|clicks?)",
            ],
        }
        
        # מיפוי יחידות
        self.unit_mappings = {
            'seconds': 's',
            'second': 's',
            'minutes': 'm',
            'minute': 'm',
            'decibels': 'dB',
            'decibel': 'dB',
            'db': 'dB',
            'percent': '%',
            'hz': 'Hz',
            'khz': 'kHz',
        }
        
        # ערכי ברירת מחדל
        self.default_values = {
            CommandType.FADE: {'duration': 2.0},
            CommandType.NORMALIZE: {'target_level': -3.0, 'type': 'peak'},
            CommandType.VOLUME: {'change': 0.0},
            CommandType.NOISE_REDUCTION: {'amount': 50.0},
        }

    async def interpret_command(self, command_text: str, context: Optional[Dict] = None) -> ParsedCommand:
        """
        פרשנות פקודה בשפה טבעית
        
        Args:
            command_text: טקסט הפקודה
            context: הקשר נוסף (קובץ אודיו, הגדרות וכו')
            
        Returns:
            ParsedCommand: פקודה מפורשת
        """
        try:
            self.logger.info(f"Interpreting command: {command_text}")
            
            # ניקוי וטקסט רגיל
            normalized_text = self._normalize_text(command_text)
            
            # ניסיון פרשנות עם דפוסים
            pattern_result = self._parse_with_patterns(normalized_text)
            
            if pattern_result.command_type != CommandType.UNKNOWN:
                self.logger.info(f"Command parsed with patterns: {pattern_result.command_type}")
                return pattern_result
            
            # אם הדפוסים לא עבדו, נשתמש ב-LLM
            llm_result = await self._parse_with_llm(command_text, context)
            
            if llm_result:
                self.logger.info(f"Command parsed with LLM: {llm_result.command_type}")
                return llm_result
            
            # אם כלום לא עבד, נחזיר פקודה לא מזוהה
            return ParsedCommand(
                command_type=CommandType.UNKNOWN,
                confidence=0.0,
                parameters=[],
                original_text=command_text,
                normalized_text=normalized_text,
                errors=["Could not interpret the command"],
                suggestions=self._generate_suggestions(normalized_text)
            )
            
        except Exception as e:
            self.logger.error(f"Error interpreting command: {e}")
            return ParsedCommand(
                command_type=CommandType.UNKNOWN,
                confidence=0.0,
                parameters=[],
                original_text=command_text,
                normalized_text=command_text,
                errors=[f"Error parsing command: {str(e)}"]
            )

    def _normalize_text(self, text: str) -> str:
        """נרמול טקסט הפקודה"""
        # המרה לאותיות קטנות
        text = text.lower().strip()
        
        # הסרת סימני פיסוק מיותרים
        text = re.sub(r'[^\w\s\-\+\.\:]+', ' ', text)
        
        # הסרת רווחים מיותרים
        text = re.sub(r'\s+', ' ', text)
        
        return text

    def _parse_with_patterns(self, text: str) -> ParsedCommand:
        """פרשנות עם דפוסי regex"""
        
        for command_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    parameters = self._extract_parameters_from_match(
                        command_type, match, text
                    )
                    
                    return ParsedCommand(
                        command_type=command_type,
                        confidence=0.9,  # אמינות גבוהה לדפוסים
                        parameters=parameters,
                        original_text=text,
                        normalized_text=text
                    )
        
        return ParsedCommand(
            command_type=CommandType.UNKNOWN,
            confidence=0.0,
            parameters=[],
            original_text=text,
            normalized_text=text
        )

    def _extract_parameters_from_match(self, command_type: CommandType, match: re.Match, text: str) -> List[CommandParameter]:
        """חילוץ פרמטרים מתוצאת regex"""
        parameters = []
        
        try:
            if command_type == CommandType.TRIM:
                if "first" in text or "beginning" in text:
                    # חיתוך מההתחלה
                    duration = float(match.group(1))
                    unit = self._normalize_unit(match.group(2) if len(match.groups()) > 1 else 's')
                    
                    parameters.append(CommandParameter(
                        name="start_time",
                        type=ParameterType.TIME,
                        value=0.0,
                        unit="s"
                    ))
                    parameters.append(CommandParameter(
                        name="duration",
                        type=ParameterType.TIME,
                        value=self._convert_to_seconds(duration, unit),
                        unit="s"
                    ))
                    
                elif "last" in text or "end" in text:
                    # חיתוך מהסוף
                    duration = float(match.group(1))
                    unit = self._normalize_unit(match.group(2) if len(match.groups()) > 1 else 's')
                    
                    parameters.append(CommandParameter(
                        name="end_offset",
                        type=ParameterType.TIME,
                        value=self._convert_to_seconds(duration, unit),
                        unit="s"
                    ))
                    
                elif "from" in text and "to" in text:
                    # חיתוך בין זמנים
                    start_time = self._parse_time(match.group(1))
                    end_time = self._parse_time(match.group(2))
                    
                    parameters.append(CommandParameter(
                        name="start_time",
                        type=ParameterType.TIME,
                        value=start_time,
                        unit="s"
                    ))
                    parameters.append(CommandParameter(
                        name="end_time",
                        type=ParameterType.TIME,
                        value=end_time,
                        unit="s"
                    ))
            
            elif command_type == CommandType.VOLUME:
                value = float(match.group(1))
                
                # זיהוי סוג השינוי
                if "increase" in text or "boost" in text or "raise" in text:
                    value = abs(value)
                elif "decrease" in text or "lower" in text or "reduce" in text:
                    value = -abs(value)
                
                # זיהוי יחידה
                unit = "dB"
                if "%" in text or "percent" in text:
                    unit = "%"
                
                parameters.append(CommandParameter(
                    name="volume_change",
                    type=ParameterType.VOLUME_DB if unit == "dB" else ParameterType.PERCENTAGE,
                    value=value,
                    unit=unit
                ))
            
            elif command_type == CommandType.FADE:
                if match.groups():
                    duration = float(match.group(1))
                else:
                    duration = self.default_values[CommandType.FADE]['duration']
                
                fade_type = "in" if "fade in" in text else "out" if "fade out" in text else "both"
                
                parameters.append(CommandParameter(
                    name="duration",
                    type=ParameterType.TIME,
                    value=duration,
                    unit="s"
                ))
                parameters.append(CommandParameter(
                    name="type",
                    type=ParameterType.STRING,
                    value=fade_type
                ))
            
            elif command_type == CommandType.NORMALIZE:
                if match.groups():
                    target_level = float(match.group(1))
                else:
                    target_level = self.default_values[CommandType.NORMALIZE]['target_level']
                
                norm_type = "rms" if "rms" in text else "peak"
                
                parameters.append(CommandParameter(
                    name="target_level",
                    type=ParameterType.VOLUME_DB,
                    value=target_level,
                    unit="dB"
                ))
                parameters.append(CommandParameter(
                    name="type",
                    type=ParameterType.STRING,
                    value=norm_type
                ))
            
            elif command_type == CommandType.NOISE_REDUCTION:
                # ברירת מחדל לכמות הפחתת רעש
                amount = self.default_values[CommandType.NOISE_REDUCTION]['amount']
                
                parameters.append(CommandParameter(
                    name="amount",
                    type=ParameterType.PERCENTAGE,
                    value=amount,
                    unit="%"
                ))
                
                # זיהוי סוג הרעש
                noise_type = "auto"
                if "hum" in text:
                    noise_type = "hum"
                elif "hiss" in text:
                    noise_type = "hiss"
                elif "click" in text:
                    noise_type = "click"
                
                parameters.append(CommandParameter(
                    name="noise_type",
                    type=ParameterType.STRING,
                    value=noise_type
                ))
        
        except (ValueError, IndexError) as e:
            self.logger.warning(f"Error extracting parameters: {e}")
            # החזרת פרמטר עם שגיאה
            parameters.append(CommandParameter(
                name="error",
                type=ParameterType.STRING,
                value=str(e),
                valid=False,
                error_message=f"Could not parse parameter: {e}"
            ))
        
        return parameters

    async def _parse_with_llm(self, command_text: str, context: Optional[Dict] = None) -> Optional[ParsedCommand]:
        """פרשנות עם LLM"""
        try:
            # הכנת prompt ל-LLM
            system_prompt = self._create_llm_system_prompt()
            user_prompt = self._create_llm_user_prompt(command_text, context)
            
            # שליחת בקשה ל-LLM
            response = await self.llm_service.generate_response(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1  # טמפרטורה נמוכה לדיוק
            )
            
            if not response or not response.get('content'):
                return None
            
            # פרשנות תגובת ה-LLM
            return self._parse_llm_response(response['content'], command_text)
            
        except Exception as e:
            self.logger.error(f"Error parsing with LLM: {e}")
            return None

    def _create_llm_system_prompt(self) -> str:
        """יצירת system prompt ל-LLM"""
        return """You are an expert audio command interpreter. Your job is to parse natural language audio editing commands and return structured JSON.

Supported command types:
- trim: Cut/remove parts of audio
- volume: Change volume levels
- fade: Add fade in/out effects
- normalize: Normalize audio levels
- noise_reduction: Remove background noise
- eq: Equalization
- reverb: Add reverb effects
- delay: Add delay/echo
- compress: Dynamic range compression
- convert: Format conversion
- analyze: Audio analysis

For each command, return JSON with:
{
  "command_type": "command_name",
  "confidence": 0.0-1.0,
  "parameters": [
    {
      "name": "parameter_name",
      "type": "time|volume_db|percentage|frequency|boolean|string|number",
      "value": actual_value,
      "unit": "s|dB|%|Hz|etc"
    }
  ],
  "warnings": ["warning messages"],
  "suggestions": ["alternative interpretations"]
}

Be precise with parameter extraction and validation."""

    def _create_llm_user_prompt(self, command_text: str, context: Optional[Dict] = None) -> str:
        """יצירת user prompt ל-LLM"""
        prompt = f"Parse this audio command: '{command_text}'"
        
        if context:
            if 'file_info' in context:
                file_info = context['file_info']
                prompt += f"\n\nAudio file context:"
                prompt += f"\n- Duration: {file_info.get('duration', 'unknown')}"
                prompt += f"\n- Sample rate: {file_info.get('sample_rate', 'unknown')}"
                prompt += f"\n- Channels: {file_info.get('channels', 'unknown')}"
        
        prompt += "\n\nReturn only valid JSON."
        return prompt

    def _parse_llm_response(self, response_content: str, original_text: str) -> Optional[ParsedCommand]:
        """פרשנות תגובת LLM"""
        try:
            # ניסיון לחלץ JSON מהתגובה
            json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
            if not json_match:
                return None
            
            data = json.loads(json_match.group())
            
            # המרת הנתונים ל-ParsedCommand
            command_type = CommandType(data.get('command_type', 'unknown'))
            confidence = float(data.get('confidence', 0.0))
            
            parameters = []
            for param_data in data.get('parameters', []):
                param = CommandParameter(
                    name=param_data['name'],
                    type=ParameterType(param_data['type']),
                    value=param_data['value'],
                    unit=param_data.get('unit')
                )
                parameters.append(param)
            
            return ParsedCommand(
                command_type=command_type,
                confidence=confidence,
                parameters=parameters,
                original_text=original_text,
                normalized_text=self._normalize_text(original_text),
                warnings=data.get('warnings', []),
                suggestions=data.get('suggestions', [])
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            self.logger.error(f"Error parsing LLM response: {e}")
            return None

    def validate_parameters(self, parsed_command: ParsedCommand, context: Optional[Dict] = None) -> ParsedCommand:
        """אימות פרמטרים של פקודה מפורשת"""
        validated_params = []
        errors = []
        warnings = []
        
        for param in parsed_command.parameters:
            validated_param = self._validate_single_parameter(param, parsed_command.command_type, context)
            validated_params.append(validated_param)
            
            if not validated_param.valid:
                errors.append(validated_param.error_message)
        
        # בדיקות נוספות לפי סוג הפקודה
        command_warnings = self._validate_command_logic(parsed_command, context)
        warnings.extend(command_warnings)
        
        return ParsedCommand(
            command_type=parsed_command.command_type,
            confidence=parsed_command.confidence,
            parameters=validated_params,
            original_text=parsed_command.original_text,
            normalized_text=parsed_command.normalized_text,
            suggestions=parsed_command.suggestions,
            warnings=warnings,
            errors=errors
        )

    def _validate_single_parameter(self, param: CommandParameter, command_type: CommandType, context: Optional[Dict] = None) -> CommandParameter:
        """אימות פרמטר בודד"""
        validated_param = CommandParameter(
            name=param.name,
            type=param.type,
            value=param.value,
            unit=param.unit,
            valid=True
        )
        
        try:
            if param.type == ParameterType.TIME:
                if param.value < 0:
                    validated_param.valid = False
                    validated_param.error_message = "Time cannot be negative"
                elif context and 'duration' in context:
                    max_duration = context['duration']
                    if param.value > max_duration:
                        validated_param.valid = False
                        validated_param.error_message = f"Time {param.value}s exceeds audio duration {max_duration}s"
            
            elif param.type == ParameterType.VOLUME_DB:
                if param.value > 20:
                    validated_param.valid = False
                    validated_param.error_message = "Volume boost above 20dB may cause distortion"
                elif param.value < -60:
                    validated_param.valid = False
                    validated_param.error_message = "Volume reduction below -60dB may make audio inaudible"
            
            elif param.type == ParameterType.PERCENTAGE:
                if param.value < 0 or param.value > 100:
                    validated_param.valid = False
                    validated_param.error_message = "Percentage must be between 0 and 100"
            
            elif param.type == ParameterType.FREQUENCY:
                if param.value < 20 or param.value > 20000:
                    validated_param.valid = False
                    validated_param.error_message = "Frequency must be between 20Hz and 20kHz"
        
        except (TypeError, ValueError) as e:
            validated_param.valid = False
            validated_param.error_message = f"Invalid parameter value: {e}"
        
        return validated_param

    def _validate_command_logic(self, parsed_command: ParsedCommand, context: Optional[Dict] = None) -> List[str]:
        """בדיקת לוגיקה של הפקודה"""
        warnings = []
        
        if parsed_command.command_type == CommandType.TRIM:
            # בדיקה שזמן ההתחלה קטן מזמן הסיום
            start_time = None
            end_time = None
            
            for param in parsed_command.parameters:
                if param.name == "start_time":
                    start_time = param.value
                elif param.name == "end_time":
                    end_time = param.value
            
            if start_time is not None and end_time is not None:
                if start_time >= end_time:
                    warnings.append("Start time should be less than end time")
        
        elif parsed_command.command_type == CommandType.VOLUME:
            # אזהרה על שינויי עוצמה גדולים
            for param in parsed_command.parameters:
                if param.name == "volume_change" and abs(param.value) > 10:
                    warnings.append(f"Large volume change ({param.value}dB) may affect audio quality")
        
        return warnings

    def _generate_suggestions(self, text: str) -> List[str]:
        """יצירת הצעות לפקודות לא ברורות"""
        suggestions = []
        
        # הצעות בסיסיות לפי מילות מפתח
        if any(word in text for word in ['cut', 'remove', 'delete']):
            suggestions.extend([
                "Cut the first 30 seconds",
                "Remove the last 10 seconds",
                "Trim from 1:30 to 2:45"
            ])
        
        if any(word in text for word in ['loud', 'quiet', 'volume']):
            suggestions.extend([
                "Increase volume by 6dB",
                "Decrease volume by 3dB",
                "Normalize the audio"
            ])
        
        if any(word in text for word in ['fade', 'smooth']):
            suggestions.extend([
                "Add 2-second fade in",
                "Apply fade out",
                "Add fade in and fade out"
            ])
        
        if any(word in text for word in ['noise', 'clean', 'hum']):
            suggestions.extend([
                "Remove background noise",
                "Clean up the recording",
                "Eliminate 60Hz hum"
            ])
        
        return suggestions[:5]  # מגביל ל-5 הצעות

    def _normalize_unit(self, unit: str) -> str:
        """נרמול יחידות"""
        unit = unit.lower().strip()
        return self.unit_mappings.get(unit, unit)

    def _convert_to_seconds(self, value: float, unit: str) -> float:
        """המרה לשניות"""
        unit = self._normalize_unit(unit)
        
        if unit == 'm':
            return value * 60
        elif unit == 'ms':
            return value / 1000
        else:  # ברירת מחדל - שניות
            return value

    def _parse_time(self, time_str: str) -> float:
        """פרשנות זמן בפורמטים שונים"""
        time_str = time_str.strip()
        
        # פורמט MM:SS או HH:MM:SS
        if ':' in time_str:
            parts = time_str.split(':')
            if len(parts) == 2:  # MM:SS
                minutes, seconds = map(float, parts)
                return minutes * 60 + seconds
            elif len(parts) == 3:  # HH:MM:SS
                hours, minutes, seconds = map(float, parts)
                return hours * 3600 + minutes * 60 + seconds
        
        # פורמט של מספר בלבד (שניות)
        return float(time_str)

    def get_command_help(self, command_type: Optional[CommandType] = None) -> Dict[str, Any]:
        """קבלת עזרה על פקודות"""
        if command_type:
            return self._get_specific_command_help(command_type)
        else:
            return self._get_all_commands_help()

    def _get_specific_command_help(self, command_type: CommandType) -> Dict[str, Any]:
        """עזרה לפקודה ספציפית"""
        help_data = {
            CommandType.TRIM: {
                "description": "Cut or remove parts of the audio",
                "examples": [
                    "Cut the first 30 seconds",
                    "Remove the last 10 seconds",
                    "Trim from 1:30 to 2:45",
                    "Extract from 0:30 to 1:30"
                ],
                "parameters": [
                    {"name": "start_time", "type": "time", "description": "Start time in seconds"},
                    {"name": "end_time", "type": "time", "description": "End time in seconds"},
                    {"name": "duration", "type": "time", "description": "Duration to cut"}
                ]
            },
            CommandType.VOLUME: {
                "description": "Adjust audio volume levels",
                "examples": [
                    "Increase volume by 6dB",
                    "Decrease volume by 3dB",
                    "Boost the audio by 10dB",
                    "Lower volume by 50%"
                ],
                "parameters": [
                    {"name": "volume_change", "type": "volume_db", "description": "Volume change in dB or %"}
                ]
            },
            CommandType.FADE: {
                "description": "Add fade in/out effects",
                "examples": [
                    "Add 2-second fade in",
                    "Apply 3-second fade out",
                    "Add fade in and fade out"
                ],
                "parameters": [
                    {"name": "duration", "type": "time", "description": "Fade duration in seconds"},
                    {"name": "type", "type": "string", "description": "Fade type: in, out, or both"}
                ]
            },
            CommandType.NORMALIZE: {
                "description": "Normalize audio levels",
                "examples": [
                    "Normalize the audio to -3dB",
                    "Apply peak normalization",
                    "Normalize to -20dB RMS"
                ],
                "parameters": [
                    {"name": "target_level", "type": "volume_db", "description": "Target level in dB"},
                    {"name": "type", "type": "string", "description": "Normalization type: peak or rms"}
                ]
            },
            CommandType.NOISE_REDUCTION: {
                "description": "Remove unwanted noise",
                "examples": [
                    "Remove background noise",
                    "Clean up the recording",
                    "Eliminate 60Hz hum"
                ],
                "parameters": [
                    {"name": "amount", "type": "percentage", "description": "Noise reduction amount (0-100%)"},
                    {"name": "noise_type", "type": "string", "description": "Type of noise: auto, hum, hiss, click"}
                ]
            }
        }
        
        return help_data.get(command_type, {"description": "Unknown command type"})

    def _get_all_commands_help(self) -> Dict[str, Any]:
        """עזרה לכל הפקודות"""
        return {
            "supported_commands": [cmd.value for cmd in CommandType if cmd != CommandType.UNKNOWN],
            "examples": [
                "Cut the first 30 seconds",
                "Increase volume by 6dB",
                "Add 2-second fade in",
                "Normalize the audio",
                "Remove background noise"
            ],
            "tips": [
                "Be specific with time values (e.g., '30 seconds' or '1:30')",
                "Use dB for volume changes (e.g., '+6dB' or '-3dB')",
                "Specify fade type (in, out, or both)",
                "Include target levels for normalization"
            ]
        }