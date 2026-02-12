#!/usr/bin/env python3
"""
Script para descobrir IDs e XPath dos elementos de um APK
Útil para criar configuração de teste
"""

import subprocess
import argparse
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any


def get_ui_hierarchy(device_id: str = None) -> str:
    """
    Obtém hierarquia de UI do device
    
    Args:
        device_id: ID do device (opcional)
    
    Returns:
        XML com hierarquia de UI
    """
    # Comando para dump de UI
    if device_id:
        cmd = ['adb', '-s', device_id, 'shell', 'uiautomator', 'dump', '/sdcard/ui.xml']
    else:
        cmd = ['adb', 'shell', 'uiautomator', 'dump', '/sdcard/ui.xml']
    
    print(f"📱 Obtendo hierarquia de UI...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Erro: {result.stderr}")
        return None
    
    # Baixar arquivo
    if device_id:
        pull_cmd = ['adb', '-s', device_id, 'pull', '/sdcard/ui.xml']
    else:
        pull_cmd = ['adb', 'pull', '/sdcard/ui.xml']
    
    subprocess.run(pull_cmd, capture_output=True)
    
    # Ler arquivo
    try:
        with open('ui.xml', 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ Erro ao ler UI: {e}")
        return None


def find_elements_by_text(xml_content: str, text: str) -> List[Dict[str, Any]]:
    """
    Encontra elementos por texto
    
    Args:
        xml_content: Conteúdo XML
        text: Texto a procurar
    
    Returns:
        Lista de elementos encontrados
    """
    results = []
    
    try:
        root = ET.fromstring(xml_content)
        
        for elem in root.iter():
            # Procurar por atributo text
            elem_text = elem.get('text', '')
            if text.lower() in elem_text.lower():
                results.append({
                    'type': elem.tag,
                    'text': elem_text,
                    'resource_id': elem.get('resource-id', ''),
                    'class': elem.get('class', ''),
                    'content_desc': elem.get('content-desc', ''),
                    'bounds': elem.get('bounds', '')
                })
    
    except Exception as e:
        print(f"❌ Erro ao parsear XML: {e}")
    
    return results


def find_elements_by_type(xml_content: str, element_type: str) -> List[Dict[str, Any]]:
    """
    Encontra elementos por tipo
    
    Args:
        xml_content: Conteúdo XML
        element_type: Tipo/class a procurar
    
    Returns:
        Lista de elementos encontrados
    """
    results = []
    
    try:
        root = ET.fromstring(xml_content)
        
        for elem in root.iter():
            class_name = elem.get('class', '')
            if element_type in class_name:
                results.append({
                    'type': elem.tag,
                    'text': elem.get('text', ''),
                    'resource_id': elem.get('resource-id', ''),
                    'class': class_name,
                    'content_desc': elem.get('content-desc', ''),
                    'bounds': elem.get('bounds', '')
                })
    
    except Exception as e:
        print(f"❌ Erro ao parsear XML: {e}")
    
    return results


def generate_xpath(elem_info: Dict[str, Any]) -> str:
    """
    Gera XPath para elemento
    
    Args:
        elem_info: Informações do elemento
    
    Returns:
        XPath string
    """
    resource_id = elem_info.get('resource_id', '')
    text = elem_info.get('text', '')
    class_name = elem_info.get('class', '')
    
    if resource_id:
        return f"//*[@resource-id='{resource_id}']"
    elif text:
        return f"//*[@text='{text}']"
    elif class_name:
        return f"//*[@class='{class_name}']"
    else:
        return None


def print_elements(elements: List[Dict[str, Any]], title: str = "Elementos encontrados"):
    """
    Imprime elementos formatados
    
    Args:
        elements: Lista de elementos
        title: Título
    """
    if not elements:
        print("❌ Nenhum elemento encontrado")
        return
    
    print(f"\n✅ {title} ({len(elements)} encontrados)\n")
    
    for i, elem in enumerate(elements, 1):
        print(f"{i}. {elem.get('type', 'Unknown')}")
        if elem.get('text'):
            print(f"   Texto: {elem['text']}")
        if elem.get('resource_id'):
            print(f"   ID: {elem['resource_id']}")
        if elem.get('content_desc'):
            print(f"   Descrição: {elem['content_desc']}")
        if elem.get('class'):
            print(f"   Classe: {elem['class']}")
        
        xpath = generate_xpath(elem)
        if xpath:
            print(f"   XPath: {xpath}")
        
        if elem.get('bounds'):
            print(f"   Posição: {elem['bounds']}")
        
        print()


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description='Descobra IDs e XPath dos elementos do APK',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Exemplos de uso:

  # Listar todos os botões
  python find_elements.py --type Button

  # Procurar por texto
  python find_elements.py --text "Login"

  # Usar device específico
  python find_elements.py --device ZY123ABC --text "Submit"

  # Salvar resultado em arquivo
  python find_elements.py --type EditText --output elements.txt
        '''
    )
    
    parser.add_argument('--device', type=str, help='ID do device (opcional)')
    parser.add_argument('--text', type=str, help='Procurar por texto')
    parser.add_argument('--type', type=str, help='Procurar por tipo (ex: Button, EditText)')
    parser.add_argument('--output', type=str, help='Salvar resultado em arquivo')
    parser.add_argument('--show-all', action='store_true', help='Mostrar todos os elementos')
    
    args = parser.parse_args()
    
    # Obter hierarquia de UI
    xml_content = get_ui_hierarchy(args.device)
    
    if not xml_content:
        return
    
    results = []
    
    if args.show_all:
        # Mostrar todos os elementos interativos
        print("\n📋 Todos os elementos interativos:\n")
        
        try:
            root = ET.fromstring(xml_content)
            for elem in root.iter():
                class_name = elem.get('class', '')
                if any(x in class_name for x in ['Button', 'EditText', 'CheckBox', 'RadioButton', 'TextView']):
                    print(f"• {elem.tag}")
                    if elem.get('text'):
                        print(f"  Texto: {elem.get('text')}")
                    if elem.get('resource-id'):
                        print(f"  ID: {elem.get('resource-id')}")
                    print()
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    elif args.text:
        results = find_elements_by_text(xml_content, args.text)
        print_elements(results, f"Elementos com texto '{args.text}'")
    
    elif args.type:
        results = find_elements_by_type(xml_content, args.type)
        print_elements(results, f"Elementos do tipo '{args.type}'")
    
    else:
        parser.print_help()
        return
    
    # Salvar em arquivo se solicitado
    if args.output and results:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(f"# Elementos encontrados\n\n")
            
            for elem in results:
                f.write(f"## {elem.get('type', 'Unknown')}\n")
                if elem.get('text'):
                    f.write(f"- Texto: {elem['text']}\n")
                if elem.get('resource_id'):
                    f.write(f"- ID: {elem['resource_id']}\n")
                if elem.get('content_desc'):
                    f.write(f"- Descrição: {elem['content_desc']}\n")
                
                xpath = generate_xpath(elem)
                if xpath:
                    f.write(f"- XPath: {xpath}\n")
                
                f.write("\n")
            
            print(f"\n✅ Resultado salvo em: {args.output}")


if __name__ == '__main__':
    main()
