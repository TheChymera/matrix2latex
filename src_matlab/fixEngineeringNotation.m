function str=fixEngineeringNotation(str)
  reg = regexp(str, 'e[-+]\d\d');
  while ~isempty(reg)
    i = reg(1);
    str = sprintf('%s\\e{%+03d}%s', str(1:i-1), str2num(str(i+1:i+3)), str(i+4:end));
    reg = regexp(str, 'e-\d\d');
  end
end