#test
from __future__ import absolute_import
from __future__ import print_function
import sys
import os
import pyverilog.vparser.ast as vast
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator

def main():
    number_ip = int(sys.argv[1])
    params,ports = port_init(number_ip)

    width = vast.Width( vast.IntConst('1'), vast.IntConst('0') )
    key_temp = vast.Reg('key_temp', width=width)
    rd_wr_temp = vast.Reg('rd_wr_temp')
    key_case = vast.Wire('key_case',width=width)

    assign_list = assign_stmt()           

    sens = vast.Sens(vast.Identifier('CLK'), type='posedge')
    senslist = vast.SensList([ sens ])
        
    statement1 = vast.Block([case_statement1(number_ip)])

    statement2 = vast.Block([case_statement2(number_ip)])

    always1 = vast.Always(senslist, statement1)

    always2 = vast.Always(senslist, statement2)

    items = []
    items.append(key_temp)
    items.append(rd_wr_temp)
    items.append(key_case)
    items.append(assign_list[0])
    items.append(assign_list[1])
    items.append(always1)
    items.append(always2)

    ast = vast.ModuleDef("mux_key", params, ports, items)
    
    codegen = ASTCodeGenerator()
    rslt = codegen.visit(ast)
    with open("mux_key.v", "w") as verilog_file:        
        verilog_file.write(rslt)

# Define the case statement
def case_statement1(number_ip):
    # Create cases    
    case_items = []
    concat_list= []
    for i in range(0,number_ip):
        case_items.append(vast.NonblockingSubstitution(vast.Lvalue(vast.Identifier(str(i)+': key_temp')), vast.Rvalue(vast.IntConst('IP'+str(i)))))
        concat_list.append(vast.Identifier('IP'+str(i)+'_IN'))

    case_items.append(vast.NonblockingSubstitution(vast.Lvalue(vast.Identifier('default: key_temp')), vast.Rvalue(vast.IntConst('IP0'))))
    
    concat_expr = vast.Concat(concat_list)
    # Create case statement
    case_statement = vast.CaseStatement(concat_expr, case_items)
    
    return case_statement 

def case_statement2(number_ip):
    # Create cases
    stmt_list=[]
    case_items = []
    for i in range(0,number_ip):
        stmt_list.append(vast.And(vast.Unot(vast.Identifier('IP'+str(i)+'_AR_VALID')), vast.Identifier('IP'+str(i)+'_AW_VALID')))
        case_items.append(vast.NonblockingSubstitution(vast.Lvalue(vast.Identifier(str(i)+': rd_wr_temp')), stmt_list[i]))                 
    # Create case statement
    case_statement = vast.CaseStatement(vast.Identifier('key_temp'), case_items)
    
    return case_statement 

def nested_if():    
    
    stmt_1 = vast.Block([vast.NonblockingSubstitution(vast.Lvalue(vast.Identifier('key_temp')), vast.Rvalue(vast.IntConst('IP0')))])
    stmt_2 = vast.Block([vast.NonblockingSubstitution(vast.Lvalue(vast.Identifier('key_temp')), vast.Rvalue(vast.IntConst('IP1')))])
    stmt_3 = vast.Block([vast.NonblockingSubstitution(vast.Lvalue(vast.Identifier('key_temp')), vast.Rvalue(vast.IntConst('IP2')))])

    if_stmt_4 = vast.IfStatement(vast.Eq(vast.Identifier('IP2_IN'),vast.IntConst('1')), stmt_3, stmt_1)
    
    if_stmt_3 = vast.IfStatement(vast.Eq(vast.Identifier('IP1_IN'),vast.IntConst('1')), stmt_2, if_stmt_4)
    
    if_stmt_2 = vast.IfStatement(vast.Eq(vast.Identifier('IP0_IN'),vast.IntConst('1')), stmt_2, if_stmt_3)

                                
    main_if = vast.IfStatement(vast.Unot(vast.Identifier('RST')),stmt_1,if_stmt_2) 
    
    return main_if

def assign_stmt():

    assign_list=[]

    assign_list.append(vast.Assign(
        vast.Lvalue(vast.Identifier('key_o')), 
        vast.Rvalue(vast.Identifier('key_temp'))))

    assign_list.append(vast.Assign(
        vast.Lvalue(vast.Identifier('rd_wr')), 
        vast.Rvalue(vast.Identifier('rd_wr_temp'))))        

    # print (assign_list)        
    return assign_list

def port_init(number_ip):

    clk = vast.Ioport( vast.Input('CLK') )
    rst = vast.Ioport( vast.Input('RST') )
    rd_wr = vast.Ioport(vast.Output('RD_WR'))

    ip=[]
    ip_in=[]
    ip_aw_valid=[]
    ip_ar_valid=[]
    for i in range(0,number_ip):
        ip.append(vast.Parameter("IP"+str(i), vast.Rvalue(vast.IntConst(str(i)))))
        ip_in.append(vast.Ioport(vast.Input('IP'+str(i)+'_IN')))
        ip_aw_valid.append(vast.Ioport( vast.Input('IP'+str(i)+'_AW_VALID') ))
        ip_ar_valid.append(vast.Ioport( vast.Input('IP'+str(i)+'_AR_VALID') ))

    params = vast.Paramlist(ip) 

    width = vast.Width( vast.IntConst('1'), vast.IntConst('0') )
    key_o = vast.Ioport( vast.Output('key_o', width=width) )

    ports = vast.Portlist( [clk, rst, key_o, rd_wr]+ ip_in +  ip_aw_valid + ip_ar_valid )

    return params, ports

if __name__ == '__main__':
    main()