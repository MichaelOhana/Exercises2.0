{
            "type": "json_schema",  # Specify the response format type
            "json_schema": {        # Define the expected JSON schema
                "name": "generate_exercises",  # Provide a unique name for the schema
                "type": "object",
                "properties": {
                    "exercises": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "word": {"type": "string"},
                                "fill_in_the_blank": {"type": "string"},
                                "multiple_choice": {
                                    "type": "object",
                                    "properties": {
                                        "question": {"type": "string"},
                                        "options": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        }
                                    },
                                    "required": ["question", "options"]
                                },
                                "true_false": {"type": "string"}
                            },
                            "required": ["word", "fill_in_the_blank", "multiple_choice", "true_false"]
                        }
                    }
                },
                "required": ["exercises"],
                "additionalProperties": False
            }
        }
