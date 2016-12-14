# Fase 1 - Reconocimiento de voz 
# Conceptos basicos 

El habla es un fenómeno complejo y la gente rara vez entiende cómo se produce y se percibe. La percepción ingenua es a menudo que el habla se construye con palabras, y cada palabra consiste en tonos. La realidad es muy diferente. El habla es un proceso dinamico sin partes claramente diferenciadas por lo que siempre es útil obtener un editor de sonido y mirar la grabación de voz y escucharlo. Por ejemplo:

[ Imagen ]

Todas las descripciones modernas del habla son probabílisticas. Esto significa que no hay ciertos limites entre unidades o entre palabras. La traducción del habla al texto y otras aplicaciones de habla nunca son 100% correctas. Esa idea es bastante inusual para los desarrolladores de software, que normalmente trabajamos con sistemas deterministicos. Y crea una gran cantidad de problemas especificos solo para la tecnologia del habla.

*Estructura*:

En la practica actual, la estructura del habla es la siguiente:

El habla es un flujo de audio continuo donde los estados mas estables se mezclan con estados cambiados dinamicamente. En esta secuencia de estados, se puede definir clases de sonidos mas o menos similares, o tonos. Se entiende que las palabras se contruyen de tonos pero esto no es cierto. Las propiedades acusticas de una forma de onda que corresponde a un tono pueden variar mucho dependiendo de muchos factores - el contexto del tono, el altavoz, el estilo de la voz, etc. La llamada "coarticulación" hace que los tonos suenen muy diferentes a su representacion "canonica".

Dado qe las transiciones entre palabras son mas informativas que las regiones estables, los desarrolladores a menudo hablamos de unidades subfónicas - diferentes subestados de un tono. A menudo se pueden encontrar facilmente tres o mas regiones de naturaleza diferente.

El numero tres se explica facilmente: La primera parte del tono depende de su tono anterior, la parte media es estable, y la siguiente parte depende del tono posterior. Es por eso que tipicamente hay tres estados en un tono seleccionado para el reconocimiento de voz.

A veces, los tonos se consideran en contexto. Tales tonos en contexo se llaman tritonos o incluso quintonos. Por ejemplo "u con tono izquierdo b y tono derecho d" en la palabra "bad" suena diferente desde un mismo tono "u" con el tono izquierdo b y tono derecho n en la palabra "ban". Tomemos en cuenta que a diferencia de los dophones se emparejan con el mismo rango en forma de onda de los tonos. Simplemente diferen por su nombre por que describen sonidos ligeramente diferentes.

Para fines computacionales, es util detectar partes de tritonos en lugar de tritonos completos. Por ejemplo, para crer un detector para un inicio de tritono y compartirlo a través de muchos tritonos. Toda la variedad de detectores de sonidos puede ser representada por una pequeña cantidad de distintos detectores de sonidos cortos. Usualmente se usan 4000 detectores de sonidos cortos para componer detectores para tritonos. Llamamos a esos detectores senones. La dependencia de un senone sobre el contexto podria ser mas compleja que el texto de izquierda y derecha explicada en el parrafo anterior. Puede ser una función bastante compleja definida por un árbol de decisión, o alguna otra manera.

A continución, los tonos crean sub-palabras, como silabas. A veces, las silabas se definen como "entidades reductoras estables". Para entender mejor, cuado el habla se vuelve rápido, los tonos suelen cambiar, pero las silabas siguen siendo las mismas. Además, las silabas están relacionadas con el contorno intonacional.  Las sub palabras regularmente se usan en el reconocimiento del habla de vocabulario abierto.

Las subpalabras forman palabras. Las palabras son importantes en el reconocimiento del habla por que restringen las combinaciones de tonos de manera significativa. Si hay 40 tonos y una palabra promedio tiene 7 tonos, debe haber 40^7 palabras. Afortunadamente, incluso una persona muy educada rara vez usa mas de 10 mil palabras  en su practica, lo que hace que el reconocimiento sea mas factible.

Las palabras y otros sonidos no linguisticos, se llaman rellenos (respiracion, umm, uhh, tos, estornudos), estos forman declaraciones. Son trozos separados de audio entre pausas. No necesariamente coinciden con frases, que son mas conceptos semánticos.

*Proceso de reconocimiento*:

La manera comun de reconocer el habla es la siguiente: tomamos la forma de onda, la dividimos en enunciados por silencios y tratamos de reconocer lo que se dice en cada enunciado. Para hacer esto tenemos que tomar todas las combinaciones posibles de palabras e intentar emparejarlas con el audio, despues elegimos la mejor combinación.

Hay que checar cosas importantes cuando tratamos de emparejar:

Primero que todo esto es un concepto de características. Dado que el número de parámetros es grande, hay que tratar de optimizar. Con números que se calculan a partir del habla usualmente dividiendo el habla en los fotogramas. Luego, para cada trama de longitud tipicamente 10 milisegundos, extraemos 39 numeros que representen el habla, eso se llama vector de caracteristicas. La forma de generar numeros es un tema de investigación activa. pero en el caso simple es una derivada.

En segundo lugar es un concepto de modelo. El modelo describe algún objeto matemático que reúne atributos comunes de la palabra hablada. En la practica, para el modelo de audio de senones es una mezcla gaussiana de sus tres estados - para decirlo mas simple, es un vector de caracteristicas mas probables. A partir del concepto de modelo se plantean las siguientes cuestiones: ¿que tan bueno se adapta el modelo a la practica? ¿el modelo puede ser mejor que los problemas internos del modelo? ¿que tan flexible es el modelo cuando hay un cambio de condiciones?

El modelo de lenguaje se llama Hidden Markov Model o HMM, es un modelo genérico que describe el cana de comunicación black-box. En este modelo el proceso se describe como una secuencia de estados que se cambian entre si con cierta probabilidad. Este modelo pretende describir cualquier proceso secuencial como el habla, y se ha demostrado que es realmente práctico para la de descodificación del habla,
