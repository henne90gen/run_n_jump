attribute vec3 a_Position;
attribute vec4 a_Color;
attribute vec3 a_Normal;

uniform mat4 u_Model;
uniform mat4 u_View;
uniform mat4 u_Projection;
uniform vec3 u_LightDirection;

varying vec4 v_Color;
varying vec3 v_Normal;
varying vec3 v_LightDirection;
varying vec3 v_WorldPosition;
varying vec3 v_EyeDirection;

void main() {
    mat4 ModelViewProjection = u_Projection * u_View * u_Model;
    gl_Position = ModelViewProjection * vec4(a_Position, 1);
    v_WorldPosition = (u_Model * vec4(a_Position, 1)).xyz;
    v_Color = a_Color;
    v_Normal = vec3(u_View * u_Model * vec4(a_Normal, 0.0)).xyz;

    vec3 vertexPositionCameraSpace = (u_View * u_Model * vec4(a_Position, 1)).xyz;
    v_EyeDirection = vec3(0,0,0) - vertexPositionCameraSpace;

    v_LightDirection = (u_View * vec4(u_LightDirection, 0.0)).xyz + v_EyeDirection;
}
