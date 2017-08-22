FragmentShaderPreamble = """
precision highp float;

vec2 convert_position(vec2 p1, vec2 s1, vec2 s2, vec2 d2) { return mod(floor((dot(p1 - 0.5, s1) + 0.5) / s2) + 0.5, d2); }
vec3 convert_position(vec2 p1, vec2 s1, vec3 s2, vec3 d2) { return mod(floor((dot(p1 - 0.5, s1) + 0.5) / s2) + 0.5, d2); }
vec4 convert_position(vec2 p1, vec2 s1, vec4 s2, vec4 d2) { return mod(floor((dot(p1 - 0.5, s1) + 0.5) / s2) + 0.5, d2); }
vec2 convert_position(vec3 p1, vec3 s1, vec2 s2, vec2 d2) { return mod(floor((dot(p1 - 0.5, s1) + 0.5) / s2) + 0.5, d2); }
vec3 convert_position(vec3 p1, vec3 s1, vec3 s2, vec3 d2) { return mod(floor((dot(p1 - 0.5, s1) + 0.5) / s2) + 0.5, d2); }
vec4 convert_position(vec3 p1, vec3 s1, vec4 s2, vec4 d2) { return mod(floor((dot(p1 - 0.5, s1) + 0.5) / s2) + 0.5, d2); }
vec2 convert_position(vec4 p1, vec4 s1, vec2 s2, vec2 d2) { return mod(floor((dot(p1 - 0.5, s1) + 0.5) / s2) + 0.5, d2); }
vec3 convert_position(vec4 p1, vec4 s1, vec3 s2, vec3 d2) { return mod(floor((dot(p1 - 0.5, s1) + 0.5) / s2) + 0.5, d2); }
vec4 convert_position(vec4 p1, vec4 s1, vec4 s2, vec4 d2) { return mod(floor((dot(p1 - 0.5, s1) + 0.5) / s2) + 0.5, d2); }
"""
