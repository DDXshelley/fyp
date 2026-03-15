%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%% IEEE 802.11bn Simulator  %%%%%%%%%%%%%%%%%%


% This simulator is intended for evaluating the performance in the downlink of a Multi-AP Coordination Network (MAPC)


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% Input parameters

traffic_type = 'Bursty';            % 'Poisson', 'Bursty', 'CBR'
traffic_load = 'high';          % for BE, i.e., Poisson, Bursty: 'low', 'medium' , 'high'
                                 % for CBR:  'x-y', where x-> bitrate, and y-> fps
EDCAaccessCategory = 'BE';

%%% Scenario-related
AP_number = 4;           % Number of APs
STA_number = 8;         % Number of STAs
grid_value = 40;         % Length of the scenario: grid_value x grid_value
scenario_type = 'grid';           % scenario_type: 'grid' ---> APs are placed in the centre of each subarea and STAs around them

walls = [0 grid_value grid_value/2 grid_value/2;            % Scenario design: each row contains the coordinates
    grid_value/2 grid_value/2 0 grid_value];                % of each wall segment: [x1 x2 y1 y2]


%%% System-related
TXOP_duration = 5E-3;       % Duration of a TXOP, 5.484E-03;
Pn_dBm = -95;               % Noise in dbm
Cca = -82;                  % Clear channel assessment in dBm (default Cca = -82 dBm)
BW = 80;                    % Bandwidth e.g., 20, 40, 80, 160 [in MHz]
Nss = 2;                    % Number of spatial streams
L = 12E3;                   % Number of bits per single frame



%%% Compute the number of subcarriers, Nsc, as well as the total power used depending on the bandwidth and the number of spatial streams
[MaxTxPower, Nsc] = TXpowerCalc(BW, Nss);      % tx power per spatial streams and number of subcarriers

%%% Computing the needed overheads based on the simulation system, i.e., for EDCA or CSR
%[preTX_overheadsEDCA, preTX_overheadsCSR, EDCAoverheads, CSRoverheads] = OverheadsCalc(EDCAaccessCategory);

[preTX_overheadsDistribute, preTX_overheadsCWAN, Distributeoverheads, CWANoverheads] = OverheadsCalc(EDCAaccessCategory);%2026
if TXOP_duration <= Distributeoverheads || TXOP_duration <= CWANoverheads
    error(['TXOP_duration must be greater than both Distribute/CWAN overheads. ', ...
           'Current TXOP_duration=', num2str(TXOP_duration*1e3,'%.3f'), ' ms, ', ...
           'Distributeoverheads=', num2str(Distributeoverheads*1e3,'%.3f'), ' ms, ', ...
           'CWANoverheads=', num2str(CWANoverheads*1e3,'%.3f'), ' ms.']);
end


rng(1);            % For reproducibility

iterations = 5;  % Each iteration represents a new deployment (new channel realization)

scheduler_labels = {'MNP', 'OP', 'TAT'};%2026
arch_labels = {'Distribute', 'CWAN'};

% Rows: iteration, Columns: scheduler (MNP/OP/TAT)
throughput_distribute = zeros(iterations, 3); % [Mbps]
throughput_cwan = zeros(iterations, 3);       % [Mbps]
delay_distribute = zeros(iterations, 3);      % [ms]
delay_cwan = zeros(iterations, 3);            % [ms]


for i = 1:iterations
    %%% Deployment-dependent %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    [AP_matrix, STA_matrix] = AP_STA_coordinates(AP_number, STA_number, scenario_type, grid_value);

    %%% Association independently of the position of STAs with respect to their corresponding APs
    association = AP_STA_Association(AP_number, STA_number, scenario_type);

    %%% Create a database with the RSSI values between all the APs and STAs and the association between APs and STAs
    [channelMatrix, RSSI_dB_vector_to_export] = GetChannelMatrix(MaxTxPower, Cca, AP_matrix, STA_matrix, scenario_type, walls);

    [per_STA_throughput_distribute, ~] = Throughput_EDCA_bianchi(AP_number, STA_number, association, RSSI_dB_vector_to_export, ...
        Pn_dBm, Nsc, Nss, TXOP_duration, Distributeoverheads, EDCAaccessCategory);
    [per_STA_throughput_cwan, ~] = Throughput_EDCA_bianchi(AP_number, STA_number, association, RSSI_dB_vector_to_export, ...
        Pn_dBm, Nsc, Nss, TXOP_duration, CWANoverheads, EDCAaccessCategory);

    
    % Offered-load baseline for traffic generation.
    % Using CWAN capacity (instead of min across architectures) avoids under-loading
    % the system and makes architecture/scheduler differences more visible.
    per_STA_EDCA_throughput_bianchi = per_STA_throughput_cwan;

     % Build coordination groups per architecture to preserve overhead-specific feasibility.
    [CGs_STAs_distribute, TxPowerMatrix_distribute] =  CGcreation(AP_number, STA_number, Distributeoverheads, Distributeoverheads,...
        Pn_dBm, Nsc, Nss, association, channelMatrix, MaxTxPower, TXOP_duration);
    [CGs_STAs_cwan, TxPowerMatrix_cwan] =  CGcreation(AP_number, STA_number, CWANoverheads, CWANoverheads,...
        Pn_dBm, Nsc, Nss, association, channelMatrix, MaxTxPower, TXOP_duration);

   
    STAs_arrivals_matrix = TrafficGenerator(STA_number, ...
            traffic_type, traffic_load, L, per_STA_EDCA_throughput_bianchi);

    timestamp_to_stop = 5;
    if timestamp_to_stop > max([STAs_arrivals_matrix{:}], [], 'all')
        error('The source of traffic generation finishes before the end of the simulation. Consider to increase the value of event_number or reduce timestamp_to_stop value');
    end


    %%% CSR MNP - Distribute
    rng(1);
    simMNP_distribute = MAPCsim(AP_number, STA_number, association, MaxTxPower, channelMatrix, timestamp_to_stop, ...
                 TXOP_duration, Pn_dBm, Nss, Nsc, preTX_overheadsDistribute, preTX_overheadsCWAN, Distributeoverheads, CWANoverheads);
    simMNP_distribute.STA_queue_timeline = STAs_arrivals_matrix;
    simMNP_distribute.simulation_system = 'CSR';
    simMNP_distribute.architecture_mode = 'Distribute';
    simMNP_distribute.scheduler = 'MNP';
    simMNP_distribute.CGs_STAs = CGs_STAs_distribute;
    simMNP_distribute.TxPowerMatrix = TxPowerMatrix_distribute;
    simMNP_distribute.accessCategory = EDCAaccessCategory;
    simMNP_distribute.Init();
    simMNP_distribute.Start();

    %%% CSR MNP - CWAN
    rng(1);
    simMNP_cwan = MAPCsim(AP_number, STA_number, association, MaxTxPower, channelMatrix, timestamp_to_stop, ...
                 TXOP_duration, Pn_dBm, Nss, Nsc, preTX_overheadsDistribute, preTX_overheadsCWAN, Distributeoverheads, CWANoverheads);
    simMNP_cwan.STA_queue_timeline = STAs_arrivals_matrix;
    simMNP_cwan.simulation_system = 'CSR';
    simMNP_cwan.architecture_mode = 'CWAN';
    simMNP_cwan.scheduler = 'MNP';
    simMNP_cwan.CGs_STAs = CGs_STAs_cwan;
    simMNP_cwan.TxPowerMatrix = TxPowerMatrix_cwan;
    simMNP_cwan.accessCategory = EDCAaccessCategory;
    simMNP_cwan.Init();
    simMNP_cwan.Start();

    %%% CSR OP - Distribute
    rng(1);
     simOP_distribute = MAPCsim(AP_number, STA_number, association, MaxTxPower, channelMatrix, timestamp_to_stop, ...
                TXOP_duration, Pn_dBm, Nss, Nsc, preTX_overheadsDistribute, preTX_overheadsCWAN, Distributeoverheads, CWANoverheads);
    simOP_distribute.STA_queue_timeline = STAs_arrivals_matrix;
    simOP_distribute.simulation_system = 'CSR';
    simOP_distribute.architecture_mode = 'Distribute';
    simOP_distribute.scheduler = 'OP';
    simOP_distribute.CGs_STAs = CGs_STAs_distribute;
    simOP_distribute.TxPowerMatrix = TxPowerMatrix_distribute;
    simOP_distribute.accessCategory = EDCAaccessCategory;
    simOP_distribute.Init();
    simOP_distribute.Start();

    %%% CSR OP - CWAN
    rng(1);
     simOP_cwan = MAPCsim(AP_number, STA_number, association, MaxTxPower, channelMatrix, timestamp_to_stop, ...
                TXOP_duration, Pn_dBm, Nss, Nsc, preTX_overheadsDistribute, preTX_overheadsCWAN, Distributeoverheads, CWANoverheads);
    simOP_cwan.STA_queue_timeline = STAs_arrivals_matrix;
    simOP_cwan.simulation_system = 'CSR';
    simOP_cwan.architecture_mode = 'CWAN';
    simOP_cwan.scheduler = 'OP';
    simOP_cwan.CGs_STAs = CGs_STAs_cwan;
    simOP_cwan.TxPowerMatrix = TxPowerMatrix_cwan;
    simOP_cwan.accessCategory = EDCAaccessCategory;
    simOP_cwan.Init();
    simOP_cwan.Start();

    %%% CSR TAT - Distribute
    rng(1);
    simTAT_distribute = MAPCsim(AP_number, STA_number, association, MaxTxPower, channelMatrix, timestamp_to_stop, ...
                TXOP_duration, Pn_dBm, Nss, Nsc, preTX_overheadsDistribute, preTX_overheadsCWAN, Distributeoverheads, CWANoverheads);
    simTAT_distribute.STA_queue_timeline = STAs_arrivals_matrix;
    simTAT_distribute.simulation_system = 'CSR';
    simTAT_distribute.architecture_mode = 'Distribute';
    simTAT_distribute.scheduler = 'TAT';
    simTAT_distribute.CGs_STAs = CGs_STAs_distribute;
    simTAT_distribute.TxPowerMatrix = TxPowerMatrix_distribute;
    simTAT_distribute.accessCategory = EDCAaccessCategory;
    simTAT_distribute.alpha_ = 1/2;
    simTAT_distribute.beta_ = 1/2;
    simTAT_distribute.Init();
    simTAT_distribute.Start();

    %%% CSR TAT - CWAN
    rng(1);
    simTAT_cwan = MAPCsim(AP_number, STA_number, association, MaxTxPower, channelMatrix, timestamp_to_stop, ...
                TXOP_duration, Pn_dBm, Nss, Nsc, preTX_overheadsDistribute, preTX_overheadsCWAN, Distributeoverheads, CWANoverheads);
    simTAT_cwan.STA_queue_timeline = STAs_arrivals_matrix;
    simTAT_cwan.simulation_system = 'CSR';
    simTAT_cwan.architecture_mode = 'CWAN';
    simTAT_cwan.scheduler = 'TAT';
    simTAT_cwan.CGs_STAs = CGs_STAs_cwan;
    simTAT_cwan.TxPowerMatrix = TxPowerMatrix_cwan;
    simTAT_cwan.accessCategory = EDCAaccessCategory;
    simTAT_cwan.alpha_ = 1/2;
    simTAT_cwan.beta_ = 1/2;
    simTAT_cwan.Init();
    simTAT_cwan.Start();

    %%% Collect metrics for grouped-bar plotting
    throughput_distribute(i, 1) = sum(cellfun(@numel, simMNP_distribute.delay_per_STA)) * L / (timestamp_to_stop * 1e6);
    throughput_distribute(i, 2) = sum(cellfun(@numel, simOP_distribute.delay_per_STA)) * L / (timestamp_to_stop * 1e6);
    throughput_distribute(i, 3) = sum(cellfun(@numel, simTAT_distribute.delay_per_STA)) * L / (timestamp_to_stop * 1e6);

    throughput_cwan(i, 1) = sum(cellfun(@numel, simMNP_cwan.delay_per_STA)) * L / (timestamp_to_stop * 1e6);
    throughput_cwan(i, 2) = sum(cellfun(@numel, simOP_cwan.delay_per_STA)) * L / (timestamp_to_stop * 1e6);
    throughput_cwan(i, 3) = sum(cellfun(@numel, simTAT_cwan.delay_per_STA)) * L / (timestamp_to_stop * 1e6);

    delay_distribute(i, 1) = mean(simMNP_distribute.delayvector) * 1e3;
    delay_distribute(i, 2) = mean(simOP_distribute.delayvector) * 1e3;
    delay_distribute(i, 3) = mean(simTAT_distribute.delayvector) * 1e3;

    delay_cwan(i, 1) = mean(simMNP_cwan.delayvector) * 1e3;
    delay_cwan(i, 2) = mean(simOP_cwan.delayvector) * 1e3;
    delay_cwan(i, 3) = mean(simTAT_cwan.delayvector) * 1e3;
end
% Mean values across all iterations for final plotting
throughput_bar_data = [mean(throughput_distribute, 1)', mean(throughput_cwan, 1)'];
delay_bar_data = [mean(delay_distribute, 1)', mean(delay_cwan, 1)'];

% 1) Throughput grouped-bar chart
figure('pos', [350, 350, 700, 450]);
bar(throughput_bar_data, 'grouped');
set(gca, 'XTickLabel', scheduler_labels, 'FontSize', 12);
xlabel('调制方式');
ylabel('吞吐量 [Mbps]');
title('MNP/OP/TAT 下 CWAN 与 Distribute 吞吐量对比');
legend(arch_labels, 'Location', 'best');
grid on;

% 2) Delay grouped-bar chart
figure('pos', [350, 350, 700, 450]);
bar(delay_bar_data, 'grouped');
set(gca, 'XTickLabel', scheduler_labels, 'FontSize', 12);
xlabel('调制方式');
ylabel('时延 [ms]');
title('MNP/OP/TAT 下 CWAN 与 Distribute 时延对比');
legend(arch_labels, 'Location', 'best');
grid on;

% Final table variables for export
CWAN_Distribute_Comparison = table(...
    scheduler_labels', throughput_bar_data(:,1), throughput_bar_data(:,2), delay_bar_data(:,1), delay_bar_data(:,2), ...
    'VariableNames', {'Scheduler', 'Distribute_Throughput_Mbps', 'CWAN_Throughput_Mbps', ...
                      'Distribute_Delay_ms', 'CWAN_Delay_ms'});
