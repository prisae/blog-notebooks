function exampleGUI
%
% Some tips regarding building a GUI from scratch, hence form a empty .m-file.
%
% Useful resources
%
% == GUI manual from Mathworks
% It contains info for both building a GUI using Matlab's GUIDE or from scratch.
% -> http://www.mathworks.com/help/pdf_doc/matlab/buildgui.pdf
%
% == 41 minimal examples
% Covering many possibilities
% -> http://www.mathworks.com/matlabcentral/fileexchange/24861-41-complete-gui-examples
%
% As stated, this is a rather small example. In a bigger project, you
% should put loads of the functions into their own files, so you can access
% them from other windows as well. I provide some comments on how to change
% some of this example in order to export functionalities into other files
% in a subfolder, e.g. ./GUI/.

%% Initialization tasks

% If you're using a subfolder (here 'GUI') to store some functions, add
% these lines. They will add the GUI-folder to the Matlab-path on the fly:
% [pathstr, ~, ~] = fileparts(which('exampleGUI'));
% addpath(pathstr, fullfile(pathstr, 'GUI'), '-BEGIN')

% Create the GUI (basically a Matlab figure), give the figure a handle-name
% (here 'hGUI'). We hide the Menubar and Toolbar that a normal Matlab
% figure has, as well as the figure number. Provide a close-function
% (@closerequest), to define what happens if the user closes the window.
hGUI = figure(...
    'NumberTitle'     , 'off',...
    'Name'            , ['exampleGUI                '...
                         'y = fct(x+phase)*amplitude; fct = {sine, cosine}'],...
    'MenuBar'         , 'none',...
    'ToolBar'         , 'none',...
    'Color'           , 'white',...
    'CloseRequestFcn' , @closereq);

%% IMPORTANT
% As this is a simple example, that contains all functionalities within
% this one file, we can easily access all data/parameters at any time.
% However, many of the functions should be put into dedicated files, to be
% accessed from other windows etc. For this reason, we store the figure
% handle in root, so we can access it from anywhere, and also from the
% Matlab Command Window.
setappdata(0, 'hGUI', hGUI);
% You can get the data from anywhere with
%   hGUI = getappdata(0, 'hGUI')
% and the functions within that with
%   alldata = getappdata(hGUI)
% or specific ones with
%   data = getappdata(hGUI, 'data')
% If you make changes to <data>, remember to store it back:
%   setappdata(hGUI, 'data', data)

% Create temporary handles structure : The stuff in this handle is not
% saved in a project, it is specific to this instance of the GUI/figure.
tmph = struct();
% Note: In this simple example, it is probably overkill to store every
% handle in tmph. However, if it becomes more complex you will be happy to
% have access to all handles!

%% 0. Settings of various buttons
% This is simple to save code later on, if you create many of the same
% element. Also, you can then change all elements at once.
% Note: I set the units to 'normalized', so it will adjust when we resize
% the GUI.
pb_set = {'Style'          'pushbutton'...
    'Units'                'normalized'};
tx_set = {'Style'          'text'...
    'HorizontalAlignment'  'center'...
    'Background'           [.95 .95 .99]...
    'Units'                'normalized'};
ed_set = {'Style'          'edit'...
    'HorizontalAlignment'  'center'...
    'Units'                'normalized'...
    'Background'           'white' };
dd_set = {'Style'          'popupmenu'...
    'Background'           'white'...
    'Units'                'normalized'};
sl_set = {'Style'          'slider'...
    'Background'           'white'...
    'Units'                'normalized'...
    'Visible'              'on'};
cb_set = {'Style'          'checkbox' ...
    'Background'           [.95 .95 .99]...
    'Value'                0 ...
    'Units'                'normalized'};
rb_set = {'Style'          'radiobutton' ...
    'Background'           'white',...
    'Value'                0 ...
    'Units'                'normalized'};
box_set = {'BorderType'    'line'...
    'BorderWidth'          1 ...
    'ForegroundColor'      [0 0 .6] ...
    'HighlightColor'       [.7 .7 1]};
ax_set = {'Parent'         hGUI ...
    'box'                  'on'...
    'Visible'              'on'};

%% 1. Toolbar
% Create our own toolbar
tmph.tb_ui = uipanel(hGUI, box_set{:},...
    'Position'        , [0.005,.005,.2,.99],...
    'BackgroundColor' , [.95 .95 .99],...
    'Title'           , '');

% Directory where the matlab icons should be
icondir = fullfile(matlabroot, '/toolbox/matlab/icons/');

% New Project
tmph.hnew = uicontrol(tmph.tb_ui, pb_set{:},...
    'Position'       , [.02, .915, .3, .08],...
    'TooltipString'  , 'New Project',...
    'CData'          , icon_read(fullfile(icondir, 'file_new.png')),...
    'Callback'       , @new_project_callback); % Callback is the function
                                              % that is called when clicked
% Open Project
tmph.hopen = uicontrol(tmph.tb_ui, pb_set{:},...
    'Position'       , [.35, .915, .3, .08],...
    'TooltipString'  , 'Open Existing Project',...
    'CData'          , icon_read(fullfile(icondir, 'file_open.png')),...
    'Callback'       , @open_project_callback);
% Save Project
tmph.hsave = uicontrol(tmph.tb_ui, pb_set{:},...
    'Position'       , [.68, .915, .3, .08],...
    'TooltipString'  , 'Save Project',...
    'CData'          , icon_read(fullfile(icondir, 'file_save.png')),...
    'Callback'       , @save_project);

% Random note on callbacks: you could provide more arguments into the
% function with: {@save_project, othervariable}; in the callback, this
% would then be
%   function save_project(hObject, ~, othervariable)
% The element in the middle is the eventhandle, see the callback of the
% radio button for an example.

%% 2. Calculation
% Here we create all elements that will change the plot

% Exclusive toggles for semilogx or linear
tmph.choose_plot = uibuttongroup(tmph.tb_ui,...
    'Background'     , 'white',...
    'Title'          , '',...
    'Position'       , [0.05 .72 .9 .15],...
    'SelectionChangeFcn', @choose_plot); % choose_plot is the fct that is
                                         % called when we click a radio button
% Linear
tmph.linear_plot = uicontrol(tmph.choose_plot, rb_set{:},...
    'String'         , ' Linear',...
    'TooltipString'  , 'Show plot on a linear scale',...  The TooltipString
    'Position'       , [.05, .6, .9, .3]);      % is shown when you hover
                                           % over the element with your mouse
% SemiLogX
tmph.semilogx_plot = uicontrol(tmph.choose_plot, rb_set{:},...
    'String'         , ' SemiLogX',...
    'TooltipString'  , 'Show plot on a semilogx-scale',...
    'Position'       , [.05, .1, .9, .3]);

% Drop-down menu for range
tmph.range = uicontrol(tmph.tb_ui, dd_set{:},...
    'Position'       , [.05, .55, .9, .1],...
    'TooltipString'  , 'Choose a plot-range',...
    'String'         , {' 0 to Pi' ' 0 to 2*Pi'},...  The individual strings
    'Callback'       , @choose_range);    % represent the items in the menu

% Checkboxes for: Sine / Cosine
% Sine
tmph.show_sine = uicontrol(tmph.tb_ui, cb_set{:},...
    'String'         , ' Sine',...
    'TooltipString'  , 'Show Sine',...
    'ForegroundColor', [1 0 0],... rgb-values: make red
    'Position'       , [.1, .46, .8, 0.08],...
    'Callback'       , @show_sinecosine);
% Cosine
tmph.show_cosine = uicontrol(tmph.tb_ui, cb_set{:},...
    'String'         , ' Cosine',...
    'TooltipString'  , 'Show Cosine',...
    'ForegroundColor', [0 0 1],...
    'Position'       , [.1, .38, .8, .08],...
    'Callback'       , @show_sinecosine);

% Amplitude: Text, Edit
tmph.tx_amp = uicontrol(tmph.tb_ui,tx_set{:},...
    'String'         , 'Amplitude (0-2):',...
    'Position'       , [.1 .22 .8 .08],...
    'TooltipString'  , 'Amplitude of Sine/Cosine');
tmph.ed_amp = uicontrol(tmph.tb_ui, ed_set{:},...
    'Position'       , [.1 .19 .8 .06],           ...
    'TooltipString'  , 'Amplitude of Sine/Cosine',...
    'String'         , ' ',...
    'Callback'       , @set_amphs);

% Phase: Text, Slider
tmph.tx_phs = uicontrol(tmph.tb_ui,tx_set{:},...
    'String'         , ' ',...
    'Position'       , [.1 .07 .8 .08],...
    'TooltipString'  , 'Amplitude of Sine/Cosine');
tmph.sl_phs = uicontrol(tmph.tb_ui, sl_set{:},...
    'Position'       , [.1 .03 .8 .06],...
    'Min'            , 0-.02,... -> This are the minimum and maximum values
    'Max'            , 2*pi+.02,... of the slider; +/- 0.02, to inlude a
    'TooltipString'  , 'Phase of Sine/Cosine',... loop-around trick.
    'SliderStep'     , [0.02/(2*pi), 0.1/(2*pi)],... -> Here you define the
    'Callback'       , @set_amphs);  % step sizes of the slider, first
% value is when you click the arrow, second value is when you click on the
% slider bar. The values are taken as percentag; so by dividing 0.02/max
% value, I set the step to 0.02.

%% 3. Plot
% Here we create the elements for the plot area

% Project-Name
tmph.hproject = uicontrol(hGUI, tx_set{:},...
    'Background'     , 'white' ,...
    'FontWeight'     , 'bold',...
    'ForegroundColor', [0 0 .6],...
    'String'         , 'Project : Project not saved!',...
    'Position'       , [.3, .9, .6, .07],...
    'TooltipString'  , 'Project Name');

tmph.plot  = axes(ax_set{:},...
    'Position'       , [.3,.12,.65,.77],...
    'Color'          , [.95 .99 .95],...
    'xlim'           , [0, 6]);
set(get(tmph.plot, 'XLabel'), 'String', 'x')
set(get(tmph.plot, 'YLabel'), 'String', 'y')

% Save tmph handles, so we can access them from anywhere
setappdata(hGUI, 'tmph', tmph)

%% 4. Set defaults (new project)
% If the GUI is started, these are the default values
data = struct();
data.projectname   = '';   % Project name
data.linear        = 1;    % Show linear
data.range         = 2;    % 0 to 2*Pi by default
data.show_sine     = 1;    % Sine on
data.show_cosine   = 1;    % Cosine on
data.amplitude     = 1;    % Default amplitude is 1
data.phase         = 0;    % Default phase is 0

% Save data, so we can access it from anywhere
setappdata(hGUI, 'data', data)

%% Call post settings
% Up to know we created all GUI elements. Now we are going to fill in the
% values. This is in a special function, so we can also call it at other
% itmes, eg after loading a project.
post_settings


% Now we have our GUI. What follows are the callback-function, hence the
% actions when a button is pressed etc.

% Again, I will always load 'tmph' and 'data' using getappdata. This would
% not be necessary, as everything is in one file. However, in this way you
% can easily extract functions and save them in another file, without
% having to change anything.

%% Callbacks

% New project (basically shortcut to close and restart hGUI)
    function new_project_callback(~, ~, ~)
        
        % Close GUI
        closereq(getappdata(0, 'hGUI'), [])
        
        % Call exampleGUI again
        exampleGUI
        
    end

% Open project (Dialog window)
    function open_project_callback(~, ~, ~)
        
        % Start uigetfile-dialog
        [project_name, project_path, ~] =...
            uigetfile({'*.mat','Project File (*.mat)'}, 'Open Project');
        
        % Check output and act upon it
        if isequal(project_name, 0) || isequal(project_path, 0)
            % do nothing, nothing was selected
        elseif (strcmp('.mat', project_name(end-3:end)) == 0)
            disp('Wrong file extension, MUST be .mat')
        else
            
            % Change path
            cd(project_path)
            
            % Load project
            load_project(project_name)
            
            % Save project
            save_project([], [], [])
            
        end
    end

% Save project
    function save_project(~, ~, ~)
        
        % Get the data
        alldat = getappdata(getappdata(0, 'hGUI'));
        
        % If there is no projectname, start 'Save As...'
        if strcmp('', alldat.data.projectname)
            % Open uiputfile-dialog
            [project_name, project_path] =...
                uiputfile({'*.mat', 'Project File (*.mat)'}, 'Save Project As');
            
            % Check output and take action
            if isequal(project_name, 0) || isequal(project_path, 0)
                proceed = 0;
            elseif strcmp('.mat', project_name(end-3:end)) == 0
                disp('Wrong file extension, MUST be .mat')
                proceed = 0;
            else
                % Change to the directory
                cd(project_path)
                
                % Store Project directory and path
                alldat.data.projectname = project_name(1:end-4);
                
                % Set Projectname
                set(alldat.tmph.hproject,  'String',...
                    ['Project: ', alldat.data.projectname] )
                
                proceed = 1;
            end
        else
            proceed = 1;
        end
        
        % We only save data, not tmph, as the handles are specific to this
        % instance, and we don't need to store them
        if proceed
            tosave = alldat.data; %#ok
            save(fullfile(pwd, [alldat.data.projectname, '.mat']),...
                '-struct', 'tosave')
        end
        
    end

% Load project
    function load_project(name)
                
        % 1. Get full file-path
        projectfile = fullfile(pwd, name);
        
        % 2. Load  saved entries
        loaddata = load(projectfile);
        
        % 3. Store the data
        setappdata(getappdata(0, 'hGUI'), 'data', loaddata) 
       
        % 4. Run post-settings
        post_settings
        
    end

% Close GUI
% I think for this simple closerequest we would not even need a function.
% However, here you could define to autosave a project, or to ask the user
% if he really wants to close the GUI, etc. Here we just delete the figure.
    function closereq(hObject, ~)
        
        % Delete figure
        delete(hObject)
        
    end

% Post settings
    function post_settings
       
        % Get data
        alldat = getappdata(getappdata(0, 'hGUI'));
        ttmph = alldat.tmph;
        tdata = alldat.data;
        
        % Set SemiLogX or Linear
        set(ttmph.semilogx_plot, 'Value',  1-tdata.linear )
        set(ttmph.linear_plot,   'Value',  tdata.linear )
        
        % Set range
        set(ttmph.range,         'Value',  tdata.range )
        
        % Set Checkboxes
        set(ttmph.show_sine,     'Value',  tdata.show_sine )
        set(ttmph.show_cosine,   'Value',  tdata.show_cosine )
        
        % Set Amplitude/Phase
        set(ttmph.ed_amp,        'String', num2str(tdata.amplitude, '% .2f') )
        set(ttmph.sl_phs,        'Value',  tdata.phase )
        set(ttmph.tx_phs,        'String', ['Phase: ', num2str(tdata.phase, '% .2f')])
        
        % Set Projectname
        if ~strcmp(tdata.projectname, '')
            set(ttmph.hproject,  'String', ['Project: ', tdata.projectname] )
        end
        
        %% Plot
        plotter
        
    end

% Plotter
    function plotter
       
        % Get data
        alldat = getappdata(getappdata(0, 'hGUI'));
        ttmph = alldat.tmph;
        tdata = alldat.data;
        
        % Clear the figure and hold the axes
        cla(ttmph.plot)
        hold(ttmph.plot, 'on')
        
        % Create x-values depending on range-choice
        if eq(tdata.range, 1)
            xvalue = linspace(0, pi);
        else
            xvalue = linspace(0, 2*pi);
        end
        
        % Set scale depending on plot-choice, adjust xvalue if log
        if tdata.linear
            set(ttmph.plot, 'xscale', 'lin')
        else
            xvalue = xvalue(2:end); % Remove the 0 value in log-scale
            set(ttmph.plot, 'xscale', 'log')
        end
        
        % If Sine and Cosine shown, fill the area in-between
        if tdata.show_sine && tdata.show_cosine
            ttmph.plfill = fill([xvalue, fliplr(xvalue)],...
                [cos(xvalue+tdata.phase),...
                fliplr(sin(xvalue+tdata.phase))]*tdata.amplitude,...
                [.99 .95 .99]);
        end
        
        % Draw horizontal dashed line at y=0
        ttmph.plzero = plot([xvalue(1), 10], [0, 0],...
            '--', 'Color', [.8 .8 .8], 'LineWidth', 2);
        
        % Plot Sine and Cosine, if requested
        if tdata.show_sine
            ttmph.plsine = plot(xvalue,...
                sin(xvalue+tdata.phase)*tdata.amplitude, 'r', 'LineWidth', 2);
        end
        if tdata.show_cosine
            ttmph.plcosine = plot(xvalue,...
                cos(xvalue+tdata.phase)*tdata.amplitude, 'b', 'LineWidth', 2);
        end
        
        % Set the limits
        xlim([xvalue(1), xvalue(end)])
        ylim([-2.05, 2.05])
        
        % Release the axes
        hold(ttmph.plot, 'off')
        
        % Store ttmph
        setappdata(getappdata(0, 'hGUI'), 'tmph', ttmph)
        
    end

% Show Sine/Cosine
    function show_sinecosine(hObject, ~, ~)
           
        % Get data
        tdata = getappdata(getappdata(0, 'hGUI'), 'data');        
        
        % Store status in plt
        if strcmp(get(hObject, 'String'), ' Sine')
            tdata.show_sine = get(hObject, 'Value');
        elseif strcmp(get(hObject, 'String'), ' Cosine')
            tdata.show_cosine = get(hObject, 'Value');
        end
        
        % Store data
        setappdata(getappdata(0, 'hGUI'), 'data', tdata)
        
        % Plot
        plotter
        
    end

% Set Amplitude/Phase
    function set_amphs(hObject, ~, ~)
              
        % Get data
        alldat = getappdata(getappdata(0, 'hGUI'));
        ttmph = alldat.tmph;
        tdata = alldat.data;
        
        % Get and store new value
        % If slider -> Phase
        % If edit -> Amplitude
        if strcmp(get(hObject, 'Style'), 'slider')
            
            % Loop-around; if value bigger than 2Pi, or smaller than 0,
            % go to the other end. Otherwise get value
            if gt(get(hObject, 'Value'), 2*pi)
                tdata.phase = 0;
            elseif lt(get(hObject, 'Value'), 0)
                tdata.phase = 2*pi;
            else
                % Round value to two decimals
                tdata.phase = round(100*get(hObject, 'Value'))./100;
            end
            
            % Set slider and string
            set(ttmph.sl_phs, 'Value', tdata.phase)
            set(ttmph.tx_phs, 'String', ['Phase: ', num2str(tdata.phase, '% .2f')])
            
        elseif strcmp(get(hObject, 'Style'), 'edit')
            
            % Round value to two decimals
            ed_val = round(100*str2double(get(hObject, 'String')))./100;
                     
            % Check input:
            % If NaN, set to 1
            % Limit to 0 <= amplitude <= 2
            if isnan(ed_val)
                ed_val = 1;
            elseif gt(ed_val, 2)
                ed_val = 2;
            elseif lt(ed_val, 0)
                ed_val = 0;
            end
            
            % Set edit value
            tdata.amplitude = ed_val;
            set(ttmph.ed_amp, 'String', num2str(tdata.amplitude, '% .2f'))
        end
        
        % Store data
        setappdata(getappdata(0, 'hGUI'), 'data', tdata)
        
        % Plot
        plotter
        
    end

% Choose x-range
    function choose_range(hObject, ~, ~)
        
        % Get data
        tdata = getappdata(getappdata(0, 'hGUI'), 'data');        
        
        tdata.range = get(hObject, 'Value');
        
        % Store data
        setappdata(getappdata(0, 'hGUI'), 'data', tdata)
                
        % Plot
        plotter
        
    end

% Choose plot
    function choose_plot(~, eventdata, ~)
        
        % Get data
        alldat = getappdata(getappdata(0, 'hGUI'));
        ttmph = alldat.tmph;
        tdata = alldat.data;
        
        % Reset values
        tdata.show_semilogx = 0;
        tdata.show_linear = 0;
        
        % Set new value
        if eq(eventdata.NewValue, ttmph.semilogx_plot)
            tdata.linear   = 0;
        elseif eq(eventdata.NewValue, ttmph.linear_plot)
            tdata.linear = 1;
        end
        
        % Store data
        setappdata(getappdata(0, 'hGUI'), 'data', tdata)
           
        % Plot
        plotter
        
    end

end