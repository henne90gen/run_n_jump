attribute vec2 a_Position;
attribute vec2 a_UV;

uniform vec2 u_Offset;

varying vec2 v_UV;

void main() {
    vec2 position = a_Position + u_Offset - vec2(400,300); // [0..800][0..600] -> [-400..400][-300..300]
    position /= vec2(400,300);
    gl_Position = vec4(position, 0, 1);

    v_UV = a_UV;
}
