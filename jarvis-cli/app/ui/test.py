import os
from PIL import Image
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Inicializamos la consola de Rich
console = Console()

# Caracteres ASCII ordenados del más oscuro al más claro
ASCII_CHARS = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", ".", " "]
"""
                 l~:   rviZ
           ?1Z|+>[vvzu/?]idhU!C
           -',iI"!I!~~~+_-?trxnii
        |.!n!.Ill.*j[f<~+--??Onc){                                 '<+"
     ^r^<!; 'i+;::;-!!i<+U-???Lnmw/                           Y:">>iI:~+<_~nI
    |0-> Q ;;I<"",:;l!i)>~_Y\tt[cpZQb                      ?':'Illll;`;~I.^~.`p
   .>:~}i "I;:,",:;>l!i<~+_?f//cJvmbvcz                  '"......'`''`"i,. `~:{f0
  I;<v>~i!lII;:::;;Iz.Ywi+-??ttXcz0m0*Z                 n ..    ..'^":II"l<~+<"[)|
  )?++~<>l_hpU]lIII(ikUv|}]??//czczwm0pW               X`>^        .^l!i>>">~_~{fj\
  .]?__i{bac1{nj!ii+lq1?{}t?ttzzccUmZwl.              '''``.'',,,:;II,^`l~"l??l]\]iLcJc]>,]p
 J_/??-_+~?{{U}<><<<_fYLr\-ttzZzzcmmmwY               q.'^:;;;;::,`.''I>>~_~^..????~   X+;U
cx?--?n-_++|ff_+~+++fff__[tfcccbzUwkO[                u.!i`'..',IllI;^.'.....'^???? \}:1m
 vzxr_-__------___X____|ftuccccczwkmO|                Y.......... ..;<I'...l+_f/{k_l|t
 [zxjcQku-x--+_1ftU{{Uuttz[;/1czwmkwcp                Yl<,Ii!III,'`:i->lI;:,>Z]!(d\/
  f}JfuUnxu--|ttuZtttttccvnmCQOmw#wO*C                /l+;","::Ii~+__<>~k?+!vm{??? )
   `>fttfttftt/cvvqXfxcccccwUqbwmQaaY              plr ::~l",:~++ipn}l`cz[)xxxrrx?k
     Q/fftQtttuvY'CaaMrCwcQmmmmmni?Q            .r+w    :.1CU-l'`jUI '' I-???]]] O
      `>mrjrvOZbnLhkpQ0XwmmmaZZ~Z               [}"^""^,I[Ld~I;,^`'`:}[)trrr(1~;"
        OJqwmZZqwmOZZwmwwmmObn-                             krnn-????]???]]]')"
             Y&|OOqdbhmmwqbmX                                  Xv(}}[[[}]}Q:
                 (w\+nXdk#v1
                     ')"
"""



"""
                                                                                                   
                                                                                                   
                                                                                                   
                                                                                                   
                                                                                                   
                                                                                                   
                                                                                                   
                                                                                                   
                                                                                                   
                                                                                                   
                                                         lI                                        
                                                        .1t.                                       
                               |+!+i                 i|~=Il+!I;                                    
                              :>  ;I,                   ,Ii.                                       
                               1l|l:                     lt                                        
                                                                                                   
                              ,:                                                                   
                             ,Ml!            ,:tl||Ii,                                             
                              .,        .1<|11:.    ,:;t<|,                                        
                                      ,#t::,;Mi           :*t.         .,:itIllt;,                 
                     >%%%%%%@%&     :M.  ,~~,                =l:1=W#!;,,;itti,   .>:               
                       :+++++i    .~1  i>1,;|*#.     .        ;##W>I;;1l|l1. .|: :=.               
                                 ,!t   .:.  ,=I. .:t#>*        :~+iiIIi  ,+t:+I,!l.                
                                .ll        ;!;;1~+1+!           :l;,i=1;++t<ti!l.                  
                                1~          ..  ;+i            .i+>Itl<|!|tl~,                     
                               .I;              ;!I+>      .tI|+Il~=l!!I||,                        
                              .i=.             .il|t.  :Il|lll|=!|!|l|t.                           
                           :ll+=*           ;!I|:.:llI!I||!=+I!!|lM1                               
                        ;!l!+|~==,       i||ii!|IlI+!I+<!l!+|II,  =;                               
                     ;~Il+|+!|<|++     ;<*lIII=!I!<+tl!~lIi.     ;I.                               
                  ,||i~|I~I;+I,:l*>!111l<=II~*+1t+<l1ittl;   ;l:.|1    ,t!~~~~!i;.                 
                .|l,|l,1|.  ,::1!>>|1t=#~til><ti:.    ;<1|<Iil~:lI.      ......                    
                <, ,~; .:;;;iI=M#+1;i+M>t;:.          ,;:..~|,,lt                                  
               .>;   ,,,,,,:1~MM~1:,+|.                 ,+l. :*,                                   
                  .,,::,..           .+=               1<i!+M,                                     
                                       .i=!;,         .:t<l.                                       
                                           .:|>*><>**~i.            .,                             
                                     ,M.                    |=|=t  .>l|                            
                                 ;=#!#~                    :|. ;l,  .:                             
                                   :*>>>1                   I!I|;                                  
                                   |!.                                                             
                                                                                                   
                                                                                                   
                                                                                                   
                                                                                                   
                                                                                                   
                                                                                                   
                                                                                                   
                                                                                                   
                                                                                                   
                                                                                                   
                                                                                                   
                                                                                                   
                                                                                                   

"""


def generar_ascii_coloreado(ruta_imagen, ancho_nuevo=70):
    """Convierte una imagen a texto ASCII coloreado usando Rich."""
    try:
        img = Image.open(ruta_imagen)
    except FileNotFoundError:
        return Text(f"❌ No se encontró la imagen: {ruta_imagen}", style="bold red")
    except Exception as e:
        return Text(f"❌ Error al cargar la imagen: {e}", style="bold red")

    # Ajustar la proporción. Las letras en la terminal son más altas que anchas,
    # por lo que multiplicamos por un factor (aprox 0.5) para que no se vea estirada.
    ancho_orig, alto_orig = img.size
    proporcion = alto_orig / ancho_orig
    alto_nuevo = int(proporcion * ancho_nuevo * 0.5)

    # Redimensionamos la imagen
    img = img.resize((ancho_nuevo, alto_nuevo))
    img_rgb = img.convert("RGB") # Para obtener los colores
    img_gris = img.convert("L")  # Para calcular el brillo y elegir la letra

    arte_ascii = Text()

    # Recorremos cada píxel de la imagen
    for y in range(alto_nuevo):
        for x in range(ancho_nuevo):
            r, g, b = img_rgb.getpixel((x, y))
            brillo = img_gris.getpixel((x, y))

            # Mapear el brillo (0-255) a un índice de nuestra lista de caracteres
            indice = int((brillo / 255) * (len(ASCII_CHARS) - 1))
            caracter = ASCII_CHARS[indice]

            # Añadir la letra con el color rgb exacto usando la magia de Rich
            arte_ascii.append(caracter, style=f"rgb({r},{g},{b})")
        
        arte_ascii.append("\n") # Salto de línea al terminar una fila

    return arte_ascii

def main():
    console.clear()
    
    # Un encabezado super cool para tu terminal
    console.rule("[bold cyan]⚡ BIENVENIDO A MI TERMINAL CUSTOM ⚡[/bold cyan]")
    console.print(Panel("[italic]Escribe [bold yellow]'mostrar <ruta_imagen.jpg>'[/bold yellow] para ver magia.\nEscribe [bold red]'salir'[/bold red] para cerrar.[/italic]", border_style="cyan"))

    # Bucle infinito (El corazón de cualquier terminal)
    while True:
        # Aquí definimos cómo se ve el prompt (la línea donde escribes)
        comando = console.input("[bold magenta]Tú@Terminal[/bold magenta][bold white]:[/bold white][bold green]~[/bold green]$ ")

        # Lógica de comandos
        if comando.lower() in ['salir', 'exit']:
            console.print("[bold red]¡Apagando sistemas... Hasta luego![/bold red]")
            break
            
        elif comando.lower().startswith('mostrar '):
            # Extraemos la ruta de la imagen
            partes = comando.split(' ', 1)
            ruta = partes[1].strip()
            
            with console.status("[bold green]Procesando imagen...", spinner="dots"):
                ascii_img = generar_ascii_coloreado(ruta, ancho_nuevo=80)
                
            console.print(Panel(ascii_img, title=f" 🖼️ {ruta} ", border_style="blue", expand=False))
            
        elif comando.lower() == 'limpiar' or comando.lower() == 'clear':
            console.clear()
            console.rule("[bold cyan]⚡ TERMINAL CUSTOM ⚡[/bold cyan]")
            
        elif comando.strip() == '':
            continue
            
        else:
            # Aquí podrías programar comandos reales usando `os.system` o `subprocess`
            console.print(f"[yellow]Comando no reconocido:[/yellow] {comando}")

if __name__ == "__main__":
    main()