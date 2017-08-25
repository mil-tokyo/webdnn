from webdnn.backend.code_generator.allocator import Allocation
from webdnn.backend.code_generator.command_buffer import CommandBuffer


def encode_command(builder: CommandBuffer):
    generated_lines = []
    indent_level = 1
    indent_text = "    "
    inputs = []
    outputs = []
    call_option = {}

    for code in builder.codes:
        if code[0] == "declare":
            # (declare, typename, varname, initial_val, const)
            _, varname, initial_val, _ = code[1:]
            if initial_val is None:
                generated_lines.append(f"{indent_text}var {varname};")

            else:
                generated_lines.append(f"{indent_text}var {varname} = {initial_val};")

        elif code[0] == "load":
            #  (load, typename, varname, buffer_key, const)
            typename, varname, buffer_key, _ = code[1:]
            value = builder.buffer_injector.value_map[buffer_key]

            if isinstance(value, Allocation):
                if value in inputs:
                    index = inputs.index(value)

                else:
                    inputs.append(value)
                    index = len(inputs) - 1

                if typename is None:
                    generated_lines.append(f"{indent_text}{varname} = input_arrays[{index}];")

                else:
                    generated_lines.append(f"{indent_text}var {varname} = input_arrays[{index}];")

            else:
                call_option[buffer_key] = value

                if typename is None:
                    generated_lines.append(f"{indent_text}{varname} = option['{buffer_key}'];")

                else:
                    generated_lines.append(f"{indent_text}var {varname} = option['{buffer_key}'];")

        elif code[0] == "exec":
            #  (Exec, expression)
            expression, = code[1:]
            generated_lines.append(f"{indent_text}{expression}")

        elif code[0] == "enterFor":
            #  (EnterFor, counter, initial_val, max_val, step_value)
            counter, initial_val, max_val, step_value = code[1:]
            generated_lines.append(f"{indent_text}for ({counter} = {initial_val}; {counter} < {max_val}; {counter} += {step_value}) {{")
            indent_level += 1
            indent_text = "    " * indent_level

        elif code[0] == "exitFor":
            #  (ExitFor,)
            indent_level -= 1
            indent_text = "    " * indent_level
            generated_lines.append(f"{indent_text}}}")

        elif code[0] == "enterBlockScope":
            #  (EnterBlockScope,)
            generated_lines.append(f"{indent_text}(function(){{")
            indent_level += 1
            indent_text = "    " * indent_level

        elif code[0] == "exitBlockScope":
            #  (ExitBlockScope,)
            indent_level -= 1
            indent_text = "    " * indent_level
            generated_lines.append(f"{indent_text}}})();")

        elif code[0] == "comment":
            #  (comment, text)
            text, = code[1:]
            generated_lines.append(f"{indent_text}//{text}")

        else:
            raise NotImplementedError(f"Unknown OP code: {code}")

    generated_lines = "\n".join(generated_lines)

    source = f"""
%%FUNC_NAME%%: function(input_arrays, output_arrays, option) {{
{generated_lines}
}},""" \
        .replace("%%INITIAL_PARALLEL_POSITION%%", "0") \
        .replace("%%PARALLEL_SIZE%%", "1")

    return source, inputs, outputs, call_option
